from aiogram import executor
from dispatcher import dp
import handlers
from config import NAME_DB

from db import BotDB
BotDB = BotDB(NAME_DB)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
