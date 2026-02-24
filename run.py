import asyncio
import uvicorn
from webapp.app import app as webapp_app
from bot.main import main as bot_main
from database import init_db


async def run_all():
    await init_db()

    tasks = [
        asyncio.create_task(bot_main()),
        uvicorn.run(webapp_app, host="0.0.0.0", port=8000)
    ]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(run_all())