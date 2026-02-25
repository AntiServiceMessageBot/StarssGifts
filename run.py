import asyncio
import uvicorn
import threading
from webapp.app import app as webapp_app
from bot.main import main as bot_main
from database import init_db


def run_webapp():
    uvicorn.run(webapp_app, host="0.0.0.0", port=8000)


async def run_all():
    await init_db()

    # Запуск webapp в отдельном потоке
    web_thread = threading.Thread(target=run_webapp, daemon=True)
    web_thread.start()

    # Запуск бота в основном event loop
    await bot_main()


if __name__ == "__main__":
    asyncio.run(run_all())