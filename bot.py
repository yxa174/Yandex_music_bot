import logging
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from yandex_music import Client
import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("yandex_music_bot.log")],
)
log = logging.getLogger("YandexMusicBot")

HELP_MESSAGE = """🎵 <b>Бот для получения информации о треках Яндекс.Музыки</b>

Отправьте мне ссылку на трек в формате:
<code>https://music.yandex.ru/album/123456/track/789012</code>

Или сокращённый вариант:
<code>https://music.yandex.ru/track/789012</code>

Я верну:
• Название трека
• Исполнитель
• Длительность
• Альбом
• Год выпуска"""

ERROR_HELP = """❌ <b>Не удалось распознать ссылку</b>

Пожалуйста, отправьте ссылку в одном из форматов:

1️⃣ Полный формат:
<code>https://music.yandex.ru/album/123456/track/789012</code>

2️⃣ Сокращённый формат:
<code>https://music.yandex.ru/track/789012</code>

Пример реальной ссылки:
<code>https://music.yandex.ru/album/1193829/track/10994777</code>"""


def init_yandex_client():
    """Инициализирует клиент Яндекс.Музыки."""
    try:
        if config.YANDEX_MUSIC_TOKEN:
            client = Client(config.YANDEX_MUSIC_TOKEN).init()
            account = client.me
            if account:
                name = getattr(account, 'name', None) or getattr(account, 'login', 'Unknown')
                log.info(f"✅ Клиент Яндекс.Музыки авторизован как {name}")
            else:
                log.warning("⚠️ Токен принят, но не удалось получить данные аккаунта")
            return client
        else:
            client = Client().init()
            log.info("⚠️ Клиент Яндекс.Музыки инициализирован без авторизации (ограниченный доступ)")
            return client
    except Exception as e:
        log.error(f"❌ Ошибка инициализации клиента Яндекс.Музыки: {e}")
        return None


def parse_track_url(url: str) -> dict | None:
    """Парсит URL трека Яндекс.Музыки и возвращает track_id и album_id."""
    full_pattern = r"music\.yandex\.(?:ru|com)/album/(\d+)/track/(\d+)"
    short_pattern = r"music\.yandex\.(?:ru|com)/track/(\d+)"

    match = re.search(full_pattern, url)
    if match:
        return {"track_id": match.group(2), "album_id": match.group(1)}

    match = re.search(short_pattern, url)
    if match:
        return {"track_id": match.group(1), "album_id": None}

    return None


def format_track_info(track) -> str:
    """Форматирует информацию о треке в читаемый вид."""
    title = track.title or "Неизвестно"
    artists = ", ".join([a.name for a in track.artists]) if track.artists else "Неизвестно"

    duration_sec = track.duration_ms // 1000
    minutes = duration_sec // 60
    seconds = duration_sec % 60
    duration = f"{minutes}:{seconds:02d}"

    albums = track.albums or []
    album_name = albums[0].title if albums else "Не указан"
    year = albums[0].year if albums and albums[0].year else "Не указан"

    genre = track.meta_data.genre if track.meta_data and track.meta_data.genre else "Не указан"

    info = f"""🎵 <b>{title}</b>

🎤 <b>Исполнитель:</b> {artists}
⏱ <b>Длительность:</b> {duration}
💿 <b>Альбом:</b> {album_name}
📅 <b>Год:</b> {year}
🏷 <b>Жанр:</b> {genre}"""

    return info


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    log.info(f"Пользователь {update.effective_user.id} запустил бота")
    await update.message.reply_text(HELP_MESSAGE, parse_mode="HTML")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help."""
    await update.message.reply_text(HELP_MESSAGE, parse_mode="HTML")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик входящих сообщений."""
    user_message = update.message.text.strip()
    log.info(f"Получено сообщение от {update.effective_user.id}: {user_message}")

    track_data = parse_track_url(user_message)
    if not track_data:
        await update.message.reply_text(ERROR_HELP, parse_mode="HTML")
        return

    await update.message.reply_text("⏳ Ищу информацию о треке...", parse_mode="HTML")

    try:
        client = context.bot_data.get("yandex_client")
        if not client:
            await update.message.reply_text(
                "❌ Ошибка подключения к Яндекс.Музыке. Попробуйте позже.",
                parse_mode="HTML",
            )
            return

        track_id = track_data["track_id"]
        album_id = track_data["album_id"]

        if album_id:
            tracks = client.tracks([f"{track_id}:{album_id}"])
        else:
            tracks = client.tracks([track_id])

        if not tracks or not tracks[0]:
            await update.message.reply_text(
                "❌ Трек не найден. Проверьте правильность ссылки.",
                parse_mode="HTML",
            )
            return

        track = tracks[0]
        info = format_track_info(track)
        await update.message.reply_text(info, parse_mode="HTML")
        log.info(f"Успешно отправлена информация о треке для пользователя {update.effective_user.id}")

    except Exception as e:
        log.error(f"Ошибка при получении информации о треке: {e}")
        error_text = str(e)
        if "451" in error_text or "Unavailable" in error_text:
            await update.message.reply_text(
                "🔒 <b>Трек недоступен по юридическим причинам</b>\n\n"
                "Это означает, что трек заблокирован в вашем регионе из-за:\n"
                "• Ограничений авторских прав\n"
                "• Лицензионных соглашений с правообладателями\n"
                "• Географических ограничений\n\n"
                "<b>Что можно сделать:</b>\n"
                "• Попробуйте другой трек\n"
                "• Используйте треки из глобальных чартов (обычно доступны везде)\n"
                "• Проверьте доступность трека непосредственно в приложении Яндекс.Музыка\n\n"
                "<i>Пример рабочей ссылки:</i>\n"
                "<code>https://music.yandex.ru/album/1193829/track/10994777</code>",
                parse_mode="HTML",
            )
        elif "401" in error_text or "Unauthorized" in error_text:
            await update.message.reply_text(
                "🔑 <b>Ошибка авторизации в Яндекс.Музыке</b>\n\n"
                "Токен недействителен или истёк. Обновите его в .env файле.\n\n"
                "<b>Как получить новый токен:</b>\n"
                "1. Откройте music.yandex.ru в браузере\n"
                "2. Войдите в аккаунт Яндекс\n"
                "3. Откройте DevTools (F12) → Application → Cookies\n"
                "4. Найдите cookie <code>yandexmusic_token</code> или <code>session_id</code>\n"
                "5. Скопируйте значение и добавьте в .env:\n"
                "<code>YANDEX_MUSIC_TOKEN=ваш_токен</code>\n\n"
                "Подробнее: https://yandex-music.readthedocs.io/en/main/token.html",
                parse_mode="HTML",
            )
        else:
            await update.message.reply_text(
                f"❌ Произошла ошибка при получении данных:\n<code>{str(e)}</code>\n\nПопробуйте позже.",
                parse_mode="HTML",
            )


def main():
    """Запуск бота."""
    if not config.BOT_TOKEN or config.BOT_TOKEN == "your_telegram_bot_token_here":
        log.error("❌ Укажите реальный BOT_TOKEN в .env файле! Получите его у @BotFather")
        return

    log.info("🚀 Запуск бота Яндекс.Музыки...")

    yandex_client = init_yandex_client()

    application = Application.builder().token(config.BOT_TOKEN).build()
    application.bot_data["yandex_client"] = yandex_client

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    log.info("✅ Бот запущен и ожидает сообщения...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
