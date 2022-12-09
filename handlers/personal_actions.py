from aiogram import types
from dispatcher import dp
import config
import re
from bot import BotDB
import requests
from bs4 import BeautifulSoup


@dp.message_handler(commands="start")
async def start(message: types.Message):
    if not BotDB.user_exists(message.from_user.id):
        BotDB.add_user(message.from_user.id)

    await message.bot.send_message(message.from_user.id, "Добро пожаловать!")


@dp.message_handler(commands=("spent", "earned", "s", "e"), commands_prefix="/!")
async def start(message: types.Message):
    cmd_variants = (('/spent', '/s', '!spent', '!s'), ('/earned', '/e', '!earned', '!e'))
    operation = '-' if message.text.startswith(cmd_variants[0]) else '+'

    value = message.text
    for i in cmd_variants:
        for j in i:
            value = value.replace(j, '').strip()

    if len(value):
        x = re.findall(r"\d+(?:.\d+)?", value)
        if len(x):
            value = float(x[0].replace(',', '.'))

            BotDB.add_record(message.from_user.id, operation, value)

            if operation == '-':
                await message.reply("✅ Запись о <u><b>расходе</b></u> успешно внесена!")
            else:
                await message.reply("✅ Запись о <u><b>доходе</b></u> успешно внесена!")
        else:
            await message.reply("Не удалось определить сумму!")
    else:
        await message.reply("Не введена сумма!")


@dp.message_handler(commands=("history", "h"), commands_prefix="/!")
async def start(message: types.Message):
    cmd_variants = ('/history', '/h', '!history', '!h')
    within_als = {
        "day": ('today', 'day', 'сегодня', 'день'),
        "month": ('month', 'месяц'),
        "year": ('year', 'год'),
    }

    cmd = message.text
    for r in cmd_variants:
        cmd = cmd.replace(r, '').strip()

    within = 'day'
    if len(cmd):
        for k in within_als:
            for als in within_als[k]:
                if als == cmd:
                    within = k

    records = BotDB.get_records(message.from_user.id, within)

    if len(records):
        answer = f"🕘 История операций за {within_als[within][-1]}\n\n"

        for r in records:
            answer += "<b>" + ("➖ Расход" if not r[2] else "➕ Доход") + "</b>"
            answer += f" - {r[3]}"
            answer += f" <i>({r[4]})</i>\n"

        await message.reply(answer)
    else:
        await message.reply("Записей не обнаружено!")


@dp.message_handler(commands=["cryptocurrency"])
async def cryptocurrency(message: types.Message):
    headers = config.NAME_DB
    url = "https://coinmarketcap.com/"
    req = requests.get(url, headers)
    script = req.text
    soup = BeautifulSoup(script, "lxml")
    reply = "Information from CoinMarketCap\n\n"
    collection = soup.find("table", class_="h7vnx2-2 czTsgW cmc-table").find("tbody").find_all("tr")
    count = 0
    for string in collection:
        now = ""
        count += 1
        info = string.find_all("td")
        reply += str(count) + ") "
        now += info[2].text
        for i in range(10, 0, -1):
            now = now.replace(str(i), " - ")
        reply += now
        reply += ": " + info[3].text + "\n"
        if count == 10:
            break
    reply = reply.replace('Buy', '')
    await message.reply(reply)


@dp.message_handler(commands=["currency"])
async def currency(message: types.Message):
    headers = config.NAME_DB
    url = "https://www.banki.ru/products/currency/cb/"
    req = requests.get(url, headers)
    script = req.text
    soup = BeautifulSoup(script, "lxml")
    reply = "Information from Central Bank of the Russian Federation\n\n"
    dollar = soup.find("table", class_="standard-table standard-table--row-highlight").find("tbody").find_all("tr")[0].\
        find_all("td")
    euro = soup.find("table", class_="standard-table standard-table--row-highlight").find("tbody").find_all("tr")[1].\
        find_all("td")
    reply += dollar[0].text.strip() + ": " + dollar[3].text.strip() + " RUB and changes: " + \
        dollar[4].text.strip() + " today \n"
    reply += euro[0].text.strip() + ": " + euro[3].text.strip() + " RUB and changes: " + euro[4].text.strip() + " today"
    await message.reply(reply)
