# 🤖 Шпаргалка для работы с Telegram Bot на bothost.ru

## 🔑 Важная информация

- **Токен бота**: Используется временный токен из .env файла
- **Git репозиторий**: Нужно запушить изменения в GitHub
- **Хостинг**: bothost.ru
- **Python версия**: 3.11

## 📝 Структура проекта

\\\
marketplace_bot/
├── bot/              # Telegram бот на aiogram
│   ├── config.py     # Конфигурация (BOT_TOKEN, DATABASE_URL)
│   ├── handlers.py   # Обработчики команд и callback
│   ├── keyboards.py  # Клавиатуры
│   └── main.py       # Запуск бота
├── database/         # SQLAlchemy модели
│   ├── models.py     # User, Seller, Product, Order...
│   └── database.py   # Async database connection
├── webapp/           # FastAPI веб-приложение
│   └── app.py        # API эндпоинты
├── static/           # Статические файлы
├── templates/        # HTML шаблоны
├── .env              # Переменные окружения (НЕ коммитить!)
├── .env.example      # Пример .env файла
├── requirements.txt  # Зависимости
├── run.py            # Точка входа (запускает и бот, и веб)
├── bothost.yml       # Конфигурация для bothost.ru
└── Dockerfile        # Docker конфигурация
\\\

## 🚀 Как развернуть/перезапустить бота

### 1. Локальные изменения

\\\ash
# Изменить код
# Проверить локально (если есть Python)
pip install -r requirements.txt
python run.py
\\\

### 2. Запушить в GitHub

\\\ash
git add .
git commit -m "Описание изменений"
git push origin main
\\\

### 3. На bothost.ru

1. Зайти в панель bothost.ru
2. Перейти к проекту бота
3. Нажать "Пересобрать" / "Rebuild"
4. Подождать сборки (~1-2 минуты)
5. Проверить логи на ошибки

## 🔧 Решение проблем

### Бот не запускается

1. Проверить логи на bothost.ru
2. Убедиться что BOT_TOKEN в .env правильный
3. Проверить что bothost.yml содержит правильную команду:

\\\yaml
language: python
python_version: "3.11"
command: python run.py

ports:
  - 8000:8000
\\\

### Ошибка импорта модулей

Проверить requirements.txt и наличие всех зависимостей:

\\\
aiogram==3.13.1
fastapi==0.115.6
uvicorn[standard]==0.32.1
sqlalchemy==2.0.36
aiosqlite==0.20.0
python-dotenv==1.0.1
pydantic==2.10.1
pydantic-settings==2.6.1
aiofiles==24.1.0
httpx==0.28.1
\\\

### База данных не создается

Бот создаёт БД автоматически при первом запуске через init_db().

## 📦 Зависимости

- **aiogram 3.13.1** - Telegram Bot API
- **FastAPI 0.115.6** - Web API
- **SQLAlchemy 2.0.36** - ORM
- **aiosqlite 0.20.0** - Async SQLite драйвер

## 🔐 Безопасность

⚠️ **НИКОГДА НЕ КОММИТИТЬ .env файл!** 

Токен должен быть в .gitignore:

\\\
.env
*.db
*.sqlite
\\\

На bothost.ru переменные окружения устанавливаются через панель или Dockerfile.

## 🎯 Команды бота

- \/start\ - Запуск бота
- Меню: Профиль, Избранное, Корзина, История покупок
- Для администраторов: Модерация продавцов

## 🌐 API эндпоинты (webapp)

- \GET /\ - Главная страница
- \GET /catalog\ - Каталог товаров
- \GET /favorites/{telegram_id}\ - Избранное
- \GET /cart/{telegram_id}\ - Корзина
- \POST /favorites/add\ - Добавить в избранное
- \POST /favorites/remove\ - Удалить из избранного
- \POST /cart/add\ - Добавить в корзину
- \POST /cart/remove\ - Удалить из корзины
- \POST /cart/clear\ - Очистить корзину

## 📝 Быстрый чеклист перед деплоем

- [ ] Код протестирован локально
- [ ] .env в .gitignore
- [ ] all changes committed and pushed to GitHub
- [ ] bothost.yml содержит правильную команду
- [ ] requirements.txt актуален
- [ ] BOT_TOKEN правильный на bothost.ru
