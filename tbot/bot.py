"""Telegram bot for the voice agent: send a voice, then a text, get the audio back as MP3.

    python -m tbot.bot

Needs TELEGRAM_BOT_TOKEN in the .env file, see .env.example.
"""
import asyncio
import io
import logging
import os
import re
import shutil
import sys
import tempfile
import time
from functools import wraps

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler,
                          PersistenceInput, PicklePersistence, filters)

from core.voice_agent import VARIANTS, Cancelled, VoiceAgent, encode_mp3, prepare_voice, write_wav
from tbot.messages import INTRO, LANGUAGE_NAMES, MESSAGES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "tbot", "data")  # voices of the users, deleted by /forget

MAX_DOWNLOAD_BYTES = 20 * 1024 * 1024  # Telegram's limit for files a bot downloads
MAX_UPLOAD_BYTES = 50 * 1024 * 1024    # Telegram's limit for files a bot sends
MAX_CLIPS = 10
MAX_TEXT_CHARS = 20000
PROGRESS_SECONDS = 5  # how often the progress message is updated
SHORT_VOICE_SECONDS = 5
NOISY_VOICE_DB = 20

logger = logging.getLogger("tbot")
agents = {}  # variant -> loaded VoiceAgent, so each model is loaded only once


def user_folder(user_id):
    return os.path.join(DATA_DIR, str(user_id))


def clips_folder(user_id):
    return os.path.join(user_folder(user_id), "clips")


def reference_path(user_id):
    return os.path.join(user_folder(user_id), "reference.wav")


def language_of(update, context):
    chosen = context.user_data.get("language")
    if chosen:
        return chosen
    code = (update.effective_user.language_code or "").split("-")[0]
    return code if code in MESSAGES else "en"


def say(language, key, **values):
    return MESSAGES[language][key].format(**values)


def allowed_only(handler):
    """Everyone may use the bot, unless ALLOWED_USER_IDS lists the only people who may."""

    @wraps(handler)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        allowed = context.bot_data["allowed"]
        if allowed and user_id not in allowed:
            logger.info("refused user %s", user_id)
            if update.callback_query:
                await update.callback_query.answer()
            await update.effective_message.reply_text(say(language_of(update, context), "not_allowed", id=user_id))
            return
        await handler(update, context)

    return wrapped


async def show_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.effective_message.reply_text(say(language_of(update, context), "your_id", id=user_id))


def language_buttons():
    return InlineKeyboardMarkup([[InlineKeyboardButton(name, callback_data=f"language:{code}")]
                                 for code, name in LANGUAGE_NAMES.items()])


def model_buttons(language, current=None):
    return InlineKeyboardMarkup([[InlineKeyboardButton(("✓ " if v == current else "") + say(language, f"model_{v}"),
                                                       callback_data=f"model:{v}")] for v in VARIANTS])


def next_step(user_id, language):
    """Tells the user what to do now, depending on whether their voice is already saved."""
    return say(language, "next_text" if os.path.exists(reference_path(user_id)) else "next_voice")


@allowed_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(INTRO, reply_markup=language_buttons())


@allowed_only
async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(say(language_of(update, context), "welcome"))


@allowed_only
async def choose_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = language_of(update, context)
    await update.effective_message.reply_text(say(language, "choose_model"),
                                              reply_markup=model_buttons(language, context.user_data.get("variant")))


@allowed_only
async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(say(language_of(update, context), "choose_language"),
                                              reply_markup=language_buttons())


@allowed_only
async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    kind, _, value = query.data.partition(":")
    if kind == "model" and value in VARIANTS:
        context.user_data["variant"] = value
        language = language_of(update, context)
        await query.edit_message_text(say(language, "model_set", name=say(language, f"model_{value}")))
        await query.message.reply_text(next_step(update.effective_user.id, language))
    elif kind == "language" and value in MESSAGES:
        context.user_data["language"] = value
        await query.edit_message_text(say(value, "language_set"))
        if "variant" in context.user_data:
            await query.message.reply_text(next_step(update.effective_user.id, value))
        else:
            await query.message.reply_text(say(value, "choose_model"), reply_markup=model_buttons(value))


def build_voice(user_id):
    """Joins all the clips of this user into the voice that is copied, and returns what was done."""
    folder = clips_folder(user_id)
    clips = [os.path.join(folder, name) for name in sorted(os.listdir(folder))]
    with tempfile.TemporaryDirectory() as tmp:
        samples, info = prepare_voice(clips, tmp, clean=True)
    write_wav(reference_path(user_id), samples)
    return info


@allowed_only
async def on_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    language = language_of(update, context)
    user_id = update.effective_user.id
    media = message.voice or message.audio or message.document
    if media.file_size and media.file_size > MAX_DOWNLOAD_BYTES:
        await message.reply_text(say(language, "too_big"))
        return

    folder = clips_folder(user_id)
    os.makedirs(folder, exist_ok=True)
    count = len(os.listdir(folder))
    if count >= MAX_CLIPS:
        await message.reply_text(say(language, "too_many_clips", count=count))
        return

    # the file name comes from the sender, so only its extension is kept and only if it looks like one
    extension = os.path.splitext(getattr(media, "file_name", None) or "")[1].lower()
    extension = extension if re.fullmatch(r"\.[a-z0-9]{1,5}", extension) else ".ogg"
    path = os.path.join(folder, f"clip_{time.time_ns()}{extension}")

    status = await message.reply_text(say(language, "checking_voice"))
    try:
        telegram_file = await media.get_file()
        await telegram_file.download_to_drive(path)
        info = await asyncio.to_thread(build_voice, user_id)
    except Exception:
        logger.exception("voice preparation failed for user %s", user_id)
        if os.path.exists(path):
            os.remove(path)
        await edit(status, say(language, "voice_failed"))
        return

    reply = say(language, "voice_ready", clips=info["clips"], seconds=info["used_seconds"], clarity=info["snr_after"])
    if info["used_seconds"] < SHORT_VOICE_SECONDS:
        reply += say(language, "voice_short")
    if info["snr_after"] < NOISY_VOICE_DB:
        reply += say(language, "voice_noisy")
    await edit(status, reply)
    if "variant" not in context.user_data:
        await message.reply_text(say(language, "choose_model"), reply_markup=model_buttons(language))


@allowed_only
async def forget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = language_of(update, context)
    folder = user_folder(update.effective_user.id)
    if not os.path.exists(folder):
        await update.effective_message.reply_text(say(language, "nothing_to_forget"))
        return
    shutil.rmtree(folder, ignore_errors=True)
    await update.effective_message.reply_text(say(language, "forgotten"))


@allowed_only
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = language_of(update, context)
    job = context.bot_data["jobs"].get(update.effective_user.id)
    if not job:
        await update.effective_message.reply_text(say(language, "nothing_to_cancel"))
        return
    job["cancel"] = True
    await update.effective_message.reply_text(say(language, "stopping"))


async def queue_text(update, context, text):
    message = update.effective_message
    language = language_of(update, context)
    user_id = update.effective_user.id
    jobs = context.bot_data["jobs"]
    text = text.strip()
    if len(text) > MAX_TEXT_CHARS:
        await message.reply_text(say(language, "text_too_long", limit=MAX_TEXT_CHARS))
        return
    if not os.path.exists(reference_path(user_id)):
        await message.reply_text(say(language, "no_voice"))
        return
    if "variant" not in context.user_data:
        await message.reply_text(say(language, "model_first"), reply_markup=model_buttons(language))
        return
    if user_id in jobs:
        await message.reply_text(say(language, "already_working"))
        return

    status = await message.reply_text(say(language, "queued", ahead=len(jobs)))
    jobs[user_id] = {"user": user_id, "chat": message.chat_id, "text": text, "language": language, "status": status,
                     "variant": context.user_data["variant"], "voice": reference_path(user_id),
                     "done": 0, "total": 0, "cancel": False}
    context.bot_data["queue"].put_nowait(jobs[user_id])


@allowed_only
async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await queue_text(update, context, update.effective_message.text)


@allowed_only
async def on_text_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    language = language_of(update, context)
    if message.document.file_size and message.document.file_size > MAX_DOWNLOAD_BYTES:
        await message.reply_text(say(language, "too_big"))
        return
    try:
        telegram_file = await message.document.get_file()
        text = bytes(await telegram_file.download_as_bytearray()).decode("utf-8-sig")
    except (TelegramError, UnicodeDecodeError):
        await message.reply_text(say(language, "bad_text_file"))
        return
    await queue_text(update, context, text)


async def edit(message, text):
    """Showing progress must never stop the work: a failed edit (same text, network) is ignored."""
    try:
        await message.edit_text(text)
    except TelegramError as e:
        logger.debug("couldn't edit message: %s", e)


def get_agent(variant):
    if variant not in agents:
        agents[variant] = VoiceAgent(variant)
    return agents[variant]


def read_text(job):
    """Runs in a thread, as the model takes a long time."""
    agent = get_agent(job["variant"])
    job["started"] = time.time()

    def progress(done, total, piece):
        job.update(done=done, total=total)

    audio = agent.speak(job["voice"], job["text"], clean=False, on_progress=progress,
                        should_stop=lambda: job["cancel"])
    return encode_mp3(audio, agent.sample_rate), round(len(audio) / agent.sample_rate, 1)


def progress_text(job):
    language = job["language"]
    done, total = job["done"], job["total"]
    if not total:
        return say(language, "loading")
    if done >= total:
        return say(language, "finishing")
    if done:
        left = (time.time() - job["started"]) / done * (total - done)
        return say(language, "progress_eta", done=done + 1, total=total, minutes=max(1, round(left / 60)))
    return say(language, "progress", done=1, total=total)


async def run_job(application, job):
    language, status = job["language"], job["status"]
    if job["cancel"]:
        await edit(status, say(language, "cancelled"))
        return

    await edit(status, say(language, "loading"))
    reading = asyncio.create_task(asyncio.to_thread(read_text, job))
    shown = None
    while not reading.done():
        await asyncio.wait({reading}, timeout=PROGRESS_SECONDS)
        text = progress_text(job)
        if text != shown and not reading.done():
            await edit(status, text)
            shown = text

    try:
        mp3, seconds = reading.result()
    except Cancelled:
        await edit(status, say(language, "cancelled"))
        return
    except ValueError as e:
        await edit(status, str(e))
        return
    except Exception:
        logger.exception("generation failed for user %s", job["user"])
        await edit(status, say(language, "failed"))
        return

    if len(mp3) > MAX_UPLOAD_BYTES:
        await edit(status, say(language, "result_too_big"))
        return
    await application.bot.send_audio(job["chat"], io.BytesIO(mp3), filename="voice_agent.mp3", title="Voice Agent",
                                     duration=round(seconds), caption=say(language, "done", seconds=seconds))
    await status.delete()


async def worker(application):
    """Jobs run one at a time: the model isn't thread safe, and each one uses the whole processor."""
    queue, jobs = application.bot_data["queue"], application.bot_data["jobs"]
    while True:
        job = await queue.get()
        try:
            await run_job(application, job)
        except TelegramError:
            logger.exception("couldn't send the result to user %s", job["user"])
            await edit(job["status"], say(job["language"], "failed"))
        except Exception:
            logger.exception("job failed for user %s", job["user"])
        finally:
            jobs.pop(job["user"], None)


async def on_error(update, context):
    logger.error("error while handling an update", exc_info=context.error)


async def post_init(application):
    application.bot_data["queue"] = asyncio.Queue()
    application.bot_data["jobs"] = {}  # user id -> their job, one at a time per user
    application.bot_data["worker"] = asyncio.create_task(worker(application))


async def post_shutdown(application):
    application.bot_data["worker"].cancel()


def build_application(token, allowed):
    os.makedirs(DATA_DIR, exist_ok=True)
    persistence = PicklePersistence(os.path.join(DATA_DIR, "settings.pickle"),
                                    store_data=PersistenceInput(bot_data=False, chat_data=False, callback_data=False))
    application = (Application.builder().token(token).persistence(persistence).post_init(post_init)
                   .post_shutdown(post_shutdown).media_write_timeout(300).read_timeout(60).build())
    application.bot_data["allowed"] = allowed

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", show_help))
    application.add_handler(CommandHandler("id", show_id))
    application.add_handler(CommandHandler("model", choose_model))
    application.add_handler(CommandHandler("language", choose_language))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CommandHandler("forget", forget))
    application.add_handler(CallbackQueryHandler(on_button))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO | filters.Document.AUDIO, on_voice))
    application.add_handler(MessageHandler(filters.Document.TXT, on_text_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    application.add_error_handler(on_error)
    return application


def read_allowed_users(value):
    return {int(part) for part in re.split(r"[,\s]+", value or "") if part.isdigit()}


def main():
    load_dotenv(os.path.join(ROOT, ".env"))
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        sys.exit("TELEGRAM_BOT_TOKEN is missing. Copy .env.example to .env and put your bot token there.")
    allowed = read_allowed_users(os.environ.get("ALLOWED_USER_IDS"))

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)  # its request log contains the bot token

    print("The bot is running. Press Ctrl+C to stop it.")
    build_application(token, allowed).run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
