"""Everything the bot says, in the same three languages as the web page."""

LANGUAGE_NAMES = {"hy": "Հայերեն", "en": "English", "ru": "Русский"}

# the first message, before a language is chosen
INTRO = ("🎙 Բարև։ Ես հայերեն տեքստը կարդում եմ ձեր ուղարկած ձայնով։\n\n"
         "Ինչպես օգտվել՝\n"
         "1. Ընտրեք լեզուն և մոդելը։\n"
         "2. Ուղարկեք ձայնային հաղորդագրություն՝ 10-15 վայրկյան, լուռ սենյակում։\n"
         "3. Ուղարկեք տեքստը կամ .txt ֆայլ։\n"
         "4. Ստացեք աուդիոն MP3 ձևաչափով։\n\n"
         "Օգտագործեք միայն ձեր ձայնը կամ այն ձայնը, որը պատճենելու թույլտվություն ունեք։\n\n"
         "———\n\n"
         "🎙 Hello! I read Armenian text in the voice you send.\n\n"
         "How to use:\n"
         "1. Choose a language and a model.\n"
         "2. Send a voice message, 10-15 seconds in a quiet room.\n"
         "3. Send the text, or a .txt file.\n"
         "4. Get the audio back as MP3.\n\n"
         "Use only your own voice, or a voice you have permission to copy.\n\n"
         "👇 Ընտրեք լեզուն / Choose a language / Выберите язык")

MESSAGES = {
    "en": {
        "welcome": "Hello! I read Armenian text in a voice you give me.\n\n"
                   "1. Choose a model with /model.\n"
                   "2. Send a voice message or an audio file, 10-15 seconds in a quiet room.\n"
                   "3. Send the text, or a .txt file.\n"
                   "4. I send back the audio as MP3.\n\n"
                   "Use only your own voice, or a voice you have permission to copy.\n\n"
                   "/model choose the model\n/language change the language\n"
                   "/cancel stop the current audio\n/forget delete your saved voice",
        "not_allowed": "This bot is private. Your Telegram ID is {id}. "
                       "The owner can add it to ALLOWED_USER_IDS in the .env file.",
        "your_id": "Your Telegram ID is {id}.",
        "checking_voice": "Checking your voice...",
        "voice_ready": "Voice saved ({clips} clip(s), using {seconds} s, clarity {clarity} dB).\n"
                       "Now send the text. To start over with another voice, use /forget.",
        "voice_short": "\n\nThis is quite short. 10-15 seconds usually works better.",
        "voice_noisy": "\n\nThis recording is noisy, and the noise will be copied too. "
                       "A quiet room gives a much clearer result.",
        "voice_failed": "I couldn't read this audio. Please send a voice message or a wav, mp3, ogg or flac file.",
        "too_big": "This file is too big, Telegram lets me download up to 20 MB.",
        "too_many_clips": "You already have {count} clips saved. Use /forget to start over.",
        "no_voice": "First send me a voice message or an audio file.",
        "text_too_long": "This text is too long, the limit is {limit} characters.",
        "bad_text_file": "I couldn't read this file. Please send a UTF-8 .txt file.",
        "already_working": "I'm still working on your previous text. Please wait, or use /cancel.",
        "queued": "Added to the queue, {ahead} before you. Use /cancel to stop.",
        "loading": "Preparing the model, the first time takes a minute or two...",
        "progress": "Reading {done} of {total}...",
        "progress_eta": "Reading {done} of {total}, about {minutes} min left...",
        "finishing": "Finishing the audio...",
        "done": "Done: {seconds} s of audio. Send another text whenever you like.",
        "result_too_big": "The audio is too big for Telegram (over 50 MB). Please send a shorter text.",
        "cancelled": "Stopped.",
        "stopping": "Stopping...",
        "nothing_to_cancel": "Nothing is running.",
        "failed": "Something went wrong. Please try again.",
        "forgotten": "Your voice has been deleted.",
        "nothing_to_forget": "You have no saved voice.",
        "choose_model": "Choose a model:",
        "model_first": "First choose a model, then send the text again:",
        "model_set": "Model: {name}",
        "choose_language": "Choose a language:",
        "language_set": "Language: English.",
        "next_voice": "What to do now: send a voice message, 10-15 seconds in a quiet room.",
        "next_text": "What to do now: send the text you want me to read.",
        "model_run4_60k": "Natural (most natural sound)",
        "model_run5_175k": "Accurate (best pronunciation)",
        "model_run5_250k": "Latest",
        "model_tri_v1": "Trilingual (Armenian, Russian, English)",
    },
    "hy": {
        "welcome": "Բարև։ Ես հայերեն տեքստը կարդում եմ այն ձայնով, որը դուք կուղարկեք։\n\n"
                   "1. Ընտրեք մոդելը՝ /model հրամանով։\n"
                   "2. Ուղարկեք ձայնային հաղորդագրություն կամ աուդիոֆայլ՝ 10-15 վայրկյան, լուռ սենյակում։\n"
                   "3. Ուղարկեք տեքստը կամ .txt ֆայլ։\n"
                   "4. Ես կուղարկեմ աուդիոն MP3 ձևաչափով։\n\n"
                   "Օգտագործեք միայն ձեր ձայնը կամ այն ձայնը, որը պատճենելու թույլտվություն ունեք։\n\n"
                   "/model ընտրել մոդելը\n/language փոխել լեզուն\n"
                   "/cancel կանգնեցնել ընթացիկ աուդիոն\n/forget ջնջել պահված ձայնը",
        "not_allowed": "Այս բոտը մասնավոր է։ Ձեր Telegram ID-ն է՝ {id}։ "
                       "Սեփականատերը կարող է այն ավելացնել .env ֆայլի ALLOWED_USER_IDS-ում։",
        "your_id": "Ձեր Telegram ID-ն է՝ {id}։",
        "checking_voice": "Ստուգում եմ ձայնը...",
        "voice_ready": "Ձայնը պահված է ({clips} ձայնագրություն, օգտագործվում է {seconds} վրկ, հստակություն՝ {clarity} դԲ)։\n"
                       "Հիմա ուղարկեք տեքստը։ Այլ ձայնով սկսելու համար օգտագործեք /forget։",
        "voice_short": "\n\nՍա բավականին կարճ է։ 10-15 վայրկյանը սովորաբար ավելի լավ է աշխատում։",
        "voice_noisy": "\n\nԱյս ձայնագրությունն աղմկոտ է, և աղմուկը նույնպես կպատճենվի։ "
                       "Լուռ սենյակում արդյունքը շատ ավելի հստակ կլինի։",
        "voice_failed": "Չկարողացա կարդալ այս աուդիոն։ Ուղարկեք ձայնային հաղորդագրություն կամ wav, mp3, ogg, flac ֆայլ։",
        "too_big": "Ֆայլը չափազանց մեծ է, Telegram-ը թույլ է տալիս ներբեռնել մինչև 20 ՄԲ։",
        "too_many_clips": "Դուք արդեն ունեք {count} պահված ձայնագրություն։ Նորից սկսելու համար օգտագործեք /forget։",
        "no_voice": "Նախ ուղարկեք ձայնային հաղորդագրություն կամ աուդիոֆայլ։",
        "text_too_long": "Տեքստը չափազանց երկար է, սահմանը {limit} նիշ է։",
        "bad_text_file": "Չկարողացա կարդալ այս ֆայլը։ Ուղարկեք UTF-8 կոդավորմամբ .txt ֆայլ։",
        "already_working": "Դեռ աշխատում եմ ձեր նախորդ տեքստի վրա։ Սպասեք կամ օգտագործեք /cancel։",
        "queued": "Ավելացվեց հերթին, ձեզնից առաջ՝ {ahead}։ Կանգնեցնելու համար՝ /cancel։",
        "loading": "Պատրաստում եմ մոդելը, առաջին անգամ դա տևում է մեկ-երկու րոպե...",
        "progress": "Կարդում եմ {done}-ը {total}-ից...",
        "progress_eta": "Կարդում եմ {done}-ը {total}-ից, մնացել է մոտ {minutes} րոպե...",
        "finishing": "Ավարտում եմ աուդիոն...",
        "done": "Պատրաստ է՝ {seconds} վրկ աուդիո։ Կարող եք ուղարկել նոր տեքստ։",
        "result_too_big": "Աուդիոն չափազանց մեծ է Telegram-ի համար (50 ՄԲ-ից ավելի)։ Ուղարկեք ավելի կարճ տեքստ։",
        "cancelled": "Կանգնեցված է։",
        "stopping": "Կանգնեցնում եմ...",
        "nothing_to_cancel": "Ոչինչ չի ընթանում։",
        "failed": "Ինչ-որ բան սխալ գնաց։ Խնդրում եմ՝ փորձեք նորից։",
        "forgotten": "Ձեր ձայնը ջնջված է։",
        "nothing_to_forget": "Դուք պահված ձայն չունեք։",
        "choose_model": "Ընտրեք մոդելը՝",
        "model_first": "Նախ ընտրեք մոդելը, ապա նորից ուղարկեք տեքստը՝",
        "model_set": "Մոդել՝ {name}",
        "choose_language": "Ընտրեք լեզուն՝",
        "language_set": "Լեզուն՝ հայերեն։",
        "next_voice": "Հիմա ուղարկեք ձայնային հաղորդագրություն՝ 10-15 վայրկյան, լուռ սենյակում։",
        "next_text": "Հիմա ուղարկեք այն տեքստը, որը պետք է կարդամ։",
        "model_run5_175k": "Ճշգրիտ (լավագույն արտասանություն)",
        "model_run4_60k": "Բնական (ամենաբնական հնչողություն)",
        "model_run5_250k": "Վերջին",
        "model_tri_v1": "Եռալեզու (հայերեն, ռուսերեն, անգլերեն)",
    },
    "ru": {
        "welcome": "Здравствуйте! Я читаю армянский текст голосом, который вы мне пришлёте.\n\n"
                   "1. Выберите модель командой /model.\n"
                   "2. Отправьте голосовое сообщение или аудиофайл, 10-15 секунд в тихой комнате.\n"
                   "3. Отправьте текст или файл .txt.\n"
                   "4. Я пришлю аудио в формате MP3.\n\n"
                   "Используйте только свой голос или голос, на копирование которого у вас есть разрешение.\n\n"
                   "/model выбрать модель\n/language сменить язык\n"
                   "/cancel остановить текущее аудио\n/forget удалить сохранённый голос",
        "not_allowed": "Это частный бот. Ваш Telegram ID: {id}. "
                       "Владелец может добавить его в ALLOWED_USER_IDS в файле .env.",
        "your_id": "Ваш Telegram ID: {id}.",
        "checking_voice": "Проверяю голос...",
        "voice_ready": "Голос сохранён (записей: {clips}, используется {seconds} с, чёткость {clarity} дБ).\n"
                       "Теперь отправьте текст. Чтобы начать с другим голосом, используйте /forget.",
        "voice_short": "\n\nЭто довольно коротко. Обычно лучше подходят 10-15 секунд.",
        "voice_noisy": "\n\nВ этой записи есть шум, и он тоже будет скопирован. "
                       "В тихой комнате результат будет намного чище.",
        "voice_failed": "Не удалось прочитать это аудио. Отправьте голосовое сообщение или файл wav, mp3, ogg, flac.",
        "too_big": "Файл слишком большой, Telegram позволяет скачивать до 20 МБ.",
        "too_many_clips": "У вас уже сохранено записей: {count}. Чтобы начать заново, используйте /forget.",
        "no_voice": "Сначала отправьте голосовое сообщение или аудиофайл.",
        "text_too_long": "Текст слишком длинный, лимит: {limit} символов.",
        "bad_text_file": "Не удалось прочитать файл. Отправьте файл .txt в кодировке UTF-8.",
        "already_working": "Я ещё работаю над вашим предыдущим текстом. Подождите или используйте /cancel.",
        "queued": "Добавлено в очередь, перед вами: {ahead}. Чтобы остановить: /cancel.",
        "loading": "Готовлю модель, в первый раз это занимает минуту-две...",
        "progress": "Читаю {done} из {total}...",
        "progress_eta": "Читаю {done} из {total}, осталось около {minutes} мин...",
        "finishing": "Завершаю аудио...",
        "done": "Готово: {seconds} с аудио. Можете отправить новый текст.",
        "result_too_big": "Аудио слишком большое для Telegram (больше 50 МБ). Отправьте текст покороче.",
        "cancelled": "Остановлено.",
        "stopping": "Останавливаю...",
        "nothing_to_cancel": "Сейчас ничего не выполняется.",
        "failed": "Что-то пошло не так. Попробуйте ещё раз.",
        "forgotten": "Ваш голос удалён.",
        "nothing_to_forget": "У вас нет сохранённого голоса.",
        "choose_model": "Выберите модель:",
        "model_first": "Сначала выберите модель, затем отправьте текст ещё раз:",
        "model_set": "Модель: {name}",
        "choose_language": "Выберите язык:",
        "language_set": "Язык: русский.",
        "next_voice": "Что делать дальше: отправьте голосовое сообщение, 10-15 секунд в тихой комнате.",
        "next_text": "Что делать дальше: отправьте текст, который нужно прочитать.",
        "model_run5_175k": "Точный (лучшее произношение)",
        "model_run4_60k": "Естественный (самое естественное звучание)",
        "model_run5_250k": "Последний",
        "model_tri_v1": "Трёхъязычный (армянский, русский, английский)",
    },
}
