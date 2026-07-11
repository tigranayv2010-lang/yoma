# 🚀 Discord Boost Bot (Telegram)

Telegram-бот для продажи Discord Server Boosts с оплатой через CryptoBot (USDT).

## Возможности

- 🌐 Мультиязычность (RU / EN)
- 💰 Пополнение баланса через CryptoBot (USDT)
- 🛒 Покупка бустов Discord (1 мес / 3 мес)
- 📊 Просмотр наличия и цен в реальном времени
- 🛠 Админ-панель: смена цен, рассылка всем пользователям

## Быстрый старт

### 1. Клонируй репозиторий
```bash
git clone https://github.com/YOUR_USERNAME/ds-boost-bot.git
cd ds-boost-bot
```

### 2. Создай `.env` файл
```bash
cp .env.example .env
```
Заполни `.env` своими токенами:
| Переменная | Где получить |
|---|---|
| `BOT_TOKEN` | [@BotFather](https://t.me/BotFather) |
| `CRYPTO_BOT_TOKEN` | [@CryptoBot](https://t.me/CryptoBot) → Crypto Pay → API |
| `GORGONA_API_KEY` | API-ключ Gorgona |
| `ADMIN_ID` | Свой Telegram ID ([@getmyid_bot](https://t.me/getmyid_bot)) |

### 3. Установи зависимости и запусти
```bash
pip install -r requirements.txt
python bot.py
```

## Деплой через Docker

```bash
docker build -t boost-bot .
docker run -d --env-file .env --name boost-bot boost-bot
```

## Деплой на VPS (systemd)

```bash
sudo nano /etc/systemd/system/boost-bot.service
```

```ini
[Unit]
Description=Discord Boost Telegram Bot
After=network.target

[Service]
User=root
WorkingDirectory=/root/ds-boost-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=5
EnvironmentFile=/root/ds-boost-bot/.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable boost-bot
sudo systemctl start boost-bot
```

## Структура проекта

```
├── bot.py            # Основной код бота
├── requirements.txt  # Зависимости Python
├── .env.example      # Шаблон переменных окружения
├── .gitignore        # Файлы, исключённые из Git
├── Dockerfile        # Контейнеризация
├── start.bat         # Запуск на Windows (локально)
└── README.md
```

## Админ-команды

| Команда | Описание |
|---|---|
| `/admin` | Открыть админ-панель |
| Изменить цену 1m / 3m | Установить свою цену за буст |
| Рассылка | Отправить сообщение всем пользователям |
