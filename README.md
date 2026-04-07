# 🎵 Yandex Music Telegram Bot

Telegram-бот для получения информации о треках Яндекс.Музыки по ссылке.

## Возможности

- 🎤 Название трека и исполнитель
- ⏱ Длительность
- 💿 Альбом и год выпуска
- 🏷 Жанр

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yxa174/Yandex_music_bot.git
cd Yandex_music_bot
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте `.env` файл:
```env
BOT_TOKEN=ваш_токен_от_BotFather
YANDEX_MUSIC_TOKEN=ваш_токен_Яндекс_Музыки
```

## Получение токенов

### Telegram Bot Token
1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot` и следуйте инструкциям
3. Скопируйте полученный токен в `.env` как `BOT_TOKEN`

### Yandex Music Token
1. Откройте [music.yandex.ru](https://music.yandex.ru) в браузере и войдите в аккаунт
2. Откройте DevTools (F12) → Application → Cookies
3. Найдите cookie `yandexmusic_token` или `session_id`
4. Скопируйте значение в `.env` как `YANDEX_MUSIC_TOKEN`

Подробнее: [документация yandex-music](https://yandex-music.readthedocs.io/en/main/token.html)

## Запуск

```bash
python3 bot.py
```

## Использование

Отправьте боту ссылку на трек в одном из форматов:

- Полный: `https://music.yandex.ru/album/123456/track/789012`
- Сокращённый: `https://music.yandex.ru/track/789012`

## Команды

| Команда | Описание |
|---|---|
| `/start` | Запуск бота и справка |
| `/help` | Справка по использованию |

## Структура проекта

| Файл | Описание |
|---|---|
| `bot.py` | Основной файл бота |
| `config.py` | Загрузка переменных окружения |
| `requirements.txt` | Зависимости |
| `.env` | Секреты (не коммитится) |

## Зависимости

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) — Telegram Bot API
- [yandex-music](https://github.com/MarshalX/yandex-music-api) — неофициальная библиотека Яндекс.Музыки
- [python-dotenv](https://github.com/theskumar/python-dotenv) — загрузка `.env`
