# Armenian Voice Agent

Clones a voice from an audio recording and reads Armenian text in that voice, using
[mnjoyan/pocket-tts-armenian](https://huggingface.co/mnjoyan/pocket-tts-armenian).

```
core/      the voice cloning and reading, used by everything else
web/       the web page
tbot/      the Telegram bot
samples/   test audio, safe to delete
```

## Setup

Run all commands from this folder.

```bash
pip install -r requirements.txt
```

The first run downloads about 1–2 GB of model weights.

## Web page

```bash
python -m web.app
```

Then open http://localhost:7860 and follow the 3 steps:

1. **Add a voice**: upload one or several files, or record with the microphone. Noisy recordings are
   cleaned and the clearest 15 seconds are used. You can listen to the voice before and after cleanup,
   and the page tells you how clear it is.
2. **Write the text**: type it, or load a .txt file. Any length; a new line gives a longer pause.
3. **Create audio**: a progress bar shows which sentence is being read and how long is left, with a
   Stop button. The result plays on the page and downloads as **MP3**.

## Telegram bot

1. In Telegram, open **@BotFather**, send `/newbot` and copy the token it gives you.
2. Copy `.env.example` to `.env` and put the token after `TELEGRAM_BOT_TOKEN=`.
3. Start the bot:
   ```bash
   python -m tbot.bot
   ```

Everyone who finds the bot can use it. To limit it to certain people, put their numbers after
`ALLOWED_USER_IDS=` in `.env` (each person gets their number by sending `/id` to the bot) and restart it.

After `/start`, each person chooses a language and a model with buttons, and can change the model later with
`/model`. The bot reads nothing until a model is chosen. Then send a voice message or an audio file, followed by
a text or a .txt file, and it sends back an MP3.

Commands: `/model`, `/language`, `/cancel`, `/forget` (deletes your saved voice), `/id`, `/help`.

- This computer must stay on with the bot running, because the model runs here.
- Texts are read one at a time, so when many people use the bot, each one waits for those before them.
- Voices are saved in `tbot/data/` until `/forget`. Texts and results are not saved.
- Unlike the web page, what you send the bot also passes through Telegram's servers. Use the web page for
  anything confidential.

## Command line

```bash
python -m core.voice_agent --voice my_voice.wav --text "Բարև, ինչպե՞ս ես։" --out out.mp3
python -m core.voice_agent --voice my_voice.wav --text-file story.txt --out story.mp3
```

- `--voice` the voice to copy: one person, at least 5 seconds. Several short clips of the same person
  can be given (`--voice a.wav b.wav c.wav`); they are joined. Longer recordings are fine, the clearest
  15 s are used.
- `--text` or `--text-file` the text to read. Long texts are read sentence by sentence.
- `--out` `.mp3` (default `output.mp3`) or `.wav`, 24 kHz.
- `--no-clean` don't remove background noise (noise is only removed when the recording is noisy).
- `--save-voice cleaned.wav` also save the cleaned voice that is copied, to listen to it.
- `--variant` `run5_175k` (default, fewest errors), `run4_60k` (the old default, best by ear), `run5_250k`, `tri_v1` (Armenian + Russian + English).

## Going back to the old model

- **For one audio**: on the web page choose **Natural**, or on the command line add `--variant run4_60k`.
- **For good**: in `core/voice_agent.py` change `DEFAULT_VARIANT = "run5_175k"` to `DEFAULT_VARIANT = "run4_60k"`
  and restart. The bot isn't affected, as everyone chooses their own model there.

## Good to know

- **Voice quality matters most.** Noise cleanup helps, but a recording in a quiet room, close to the
  microphone, gives a much better copy than any cleanup.
- **Noisy results are cleaned too.** The model copies the noise of the voice sample, so finished audio that
  is still noisy has its rumble removed and its pauses turned down. Clean audio is left alone. To turn this off,
  set `OUTPUT_CLEAN_SNR = 0` in `core/voice_agent.py`.
- **Voice files**: wav, mp3, ogg and flac work as they are. Other formats such as m4a need
  [ffmpeg](https://ffmpeg.org/) (the web page reads them without it).
- **Speed**: on a computer without a graphics card (GPU), 1 minute of audio takes several minutes to make.
  With an NVIDIA GPU it's about real time or faster.
