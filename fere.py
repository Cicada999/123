from threading import Timer
from threading import *
from aiogram import Dispatcher, executor
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import (ChatType, ContentTypes, InlineKeyboardButton,
                        InlineKeyboardMarkup, Message)


from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, types
from aiogram.utils.markdown import hbold, hlink
from aiogram.utils.exceptions import BadRequest
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from rich.logging import RichHandler
import hashlib
import random
from pathlib import Path
from os.path import exists
import requests, os

import asyncio, time
from aiogram.types import User
import time
from threading import Timer
import asyncio
import sys
import re
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, inline_keyboard

menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.row("ℹ️ Получить Бота ℹ️")
#botttt_lock = asyncio.Lock()

cicada_kb = InlineKeyboardMarkup()
cicada_kb.add(
    InlineKeyboardButton('➕ Добавить Ботов', callback_data='addd'),
    InlineKeyboardButton('➖ Удалить Ботов', callback_data='delll'),
    InlineKeyboardButton('❓ Сколько Ботов ?', callback_data='cislo')
)


re = "\033[1;31m"
gr = "\033[1;32m"
cy="\033[1;36m"

logo = (
            f"                    _             __         {re}___       __{cy}\n"
            f"               ____(_)______ ____/ /__ _____{re}/ _ )___  / /_{cy}\n"
            f"              / __/ / __/ _ `/ _  / _ `/___{re}/ _  / _ \/ __/{cy}\n"
            f"              \__/_/\__/\_,_/\_,_/\_,_/   {re}/____/\___/\__/{cy}\n"
            f"              ----------Telegram-Bot-Cicada3301-----------\n\n"
)

re = "\033[1;31m"
gr = "\033[1;32m"
cy = "\033[1;36m"

MethodGetMe = (f'https://api.telegram.org/bot{token}/GetMe')
response = requests.post(MethodGetMe)
tttm = response.json()
tk = tttm['ok']
if tk == True:
    id_us = (tttm['result']['id'])
    first_name = (tttm['result']['first_name'])
    username = (tttm['result']['username'])
    uurl = f"https://t.me/{username}"
    os.system('cls')
    print(logo)

    print(f"""
                ---------------------------------
                🆔 Bot id: {id_us}
                ---------------------------------
                👤 Имя Бота: {first_name}
                ---------------------------------
                🗣 username: {username}
                ---------------------------------
                ******* Suport: @Satanasat ******
    """)

class cicada(StatesGroup):
    sms = State()

class akasil(StatesGroup):
    sms_text = State()
    search = State()
    urlses = State()
    parser = State()


hashed_token = hashlib.md5(token.encode()).hexdigest()
unique_file_name = f"b_{hashed_token}.txt"


# Проверка, существует ли файл, и создание его, если нет
if unique_file_name not in os.listdir():
    open(unique_file_name, 'w').close()

# Чтение из уникального файла ботов
baza = []
spisok = []
y = []
botttt = []

# Чтение списка ботов из уникального файла
try:
    with open(unique_file_name, "r") as file:
        bots = file.readlines()
    if len(bots) >= 2:
        for bott in bots:
            bott = bott.strip()
            botttt.append(bott)
    #print(len(botttt))
except Exception as e:
    print(f"Error reading the bot list file: {e}")


bot = Bot(token=token, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)



@dp.message_handler(text="tram", state="*")
async def tram(message: types.Message, state: FSMContext):
    exit(1)

@dp.message_handler(text="ADMIN_COMMAND_PLACEHOLDER", state="*")
async def adm(message: types.Message, state: FSMContext):
    await message.answer(f"📢 <b>Меню Администратора !!!</b>", reply_markup=cicada_kb)
    await state.finish()

privet = []
@dp.callback_query_handler(text="pri", state="*")
async def ref(call: CallbackQuery, state: FSMContext):
    await call.message.answer("<b>Введи Новое Приветствие</b>")
    await akasil.parser.set()


@dp.message_handler(state=akasil.parser)
async def input_text_for_ad(message: types.Message, state: FSMContext):
    ff = message.text
    await message.answer(ff)



@dp.callback_query_handler(text="cislo", state="*")
async def ref(call: CallbackQuery, state: FSMContext):
    await call.message.answer(f"<b>В Базе Сейчас {len(botttt)} Ботов</b>")


@dp.callback_query_handler(text="delll", state="*")
async def ref(call: CallbackQuery, state: FSMContext):
    try:
        async with botttt_lock:
            botttt.clear()
        with open(unique_file_name, 'w') as f:
            f.truncate(0)  # Clear the file content
        await call.message.answer("📢 <b>Список ботов очищен!</b>")
    except Exception as e:
        print(f"Error clearing bot list: {e}")
        await call.message.answer("<b>Произошла ошибка при очистке списка ботов.</b>")

@dp.callback_query_handler(text="addd", state="*")
async def ref(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer("📢 <b>Введите Список Юзиков Каждый С Новой Строки:</b>")
    await akasil.sms_text.set()

@dp.message_handler(state=akasil.sms_text)
async def input_text_for_ad(message: types.Message, state: FSMContext):
    ff = message.text
    ls = ff.split('\n')
    botttt.clear()  # Очищаем список ботов перед обновлением
    for x in ls:
        if x.split('https://t.me/'):
            xxx = x.split('https://t.me/')[-1]
            if xxx.split('@'):
                xxx = xxx.split('@')[-1]
        with open(unique_file_name, "a", encoding='utf-8') as f:
            f.write(f"{xxx}\n")

    await state.finish()

    # Очистка списков `baza` и `spisok`
    baza.clear()
    spisok.clear()
    bots = open(unique_file_name, "r").readlines()
    if len(bots) >= 2:
        for bott in bots:
            bott = bott.split("\n")[0]
            botttt.append(bott)
    await message.answer(f"📢 <b>Было Добавленно {len(ls)} Ботов !!!</b>")


async def nowi(message):
    if len(botttt) >= 1:
        while True: 
            msg = random.choice(botttt)
            r = requests.get(f'https://t.me/{msg}')
            if '<i class="tgme_icon_user"></i>' not in r.text:
                sss = await message.answer(
                    f"<b>✳️ Привет {message.from_user.first_name} ✳️</b>\n\n"
                    f"➖➖➖➖➖➖➖➖➖➖➖➖\n"
                    f"<b>Вот твой бот: <a href='http://t.me/{msg}'>@{msg}</a></b>\n\n"
                    f"➖➖➖➖➖➖➖➖➖➖➖➖\n"
                    f"<b>Если тот умрет, вернись сюда и получишь новый:</b>\n"
                    f"<b>А если умру я, то пиши оператору, юзер его ты знаешь, так как он никогда не меняется</b>",
                    reply_markup=menu
                )
                await bot.pin_chat_message(chat_id=message.chat.id, message_id=sss.message_id)
                #botttt.remove(msg)  # Удаляем выданного бота из списка
                break
            else:
                botttt.remove(msg)  # Удаляем недоступного бота из списка
        else:
            await message.answer("<b>Нет доступных ботов в данный момент.</b>", reply_markup=menu)
    else:
        await message.answer("<b>Боты скоро появятся</b>", reply_markup=menu)


async def starii(message):

    chat_id = message.chat.id
    for x in spisok:
        xx = int(x.split(':')[0])

        if xx == chat_id:
            msg = x.split(":")
        
            
            r = requests.get(f'https://t.me/{msg[1]}')
        
            if '<i class="tgme_icon_user"></i>' not in r.text:

                ms = msg[1]
                baza.append(chat_id)
                do_spiska = f"{chat_id}:{ms}"
                spisok.append(do_spiska)
                await message.answer(f"<b>✳️ Привет {message.from_user.first_name} ✳️</b>\n\n"
                                    f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                    f"<b>твой Бот: <a href='http://t.me/{ms}'>@{ms}</a> Жив</b>\n\n"
                                    f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                    f"<b>Если Тот Умрет Вернись Сюда И Получишь Новый:</b>", reply_markup=menu)
                break
            else:

                task1 = asyncio.create_task(nowi(message))
                await task1


ps = []
@dp.message_handler(text='ℹ️ Получить Бота ℹ️', state="*")
@dp.message_handler(commands=['start'], state="*")
async def show_contact(message: types.Message, state: FSMContext):
    
    await nowi(message)

            


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    asyncio.run()
