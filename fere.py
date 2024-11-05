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

import asyncio, time, aiohttp
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
botttt_lock = asyncio.Lock()

user_bots = {}
user_bots_lock = asyncio.Lock()  # Блокировка для безопасного доступа


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

async def update_bot_file():
    async with botttt_lock:  # Защита доступа к botttt
        with open(unique_file_name, "w", encoding="utf-8") as f:
            for bot in botttt:
                f.write(f"{bot}\n")

@dp.callback_query_handler(text="delll", state="*")
async def ref(call: CallbackQuery, state: FSMContext):
    try:
        async with botttt_lock:
            botttt.clear()
            baza.clear()
            spisok.clear()
        # Открываем файл в режиме 'w' и сразу закрываем, чтобы очистить его содержимое
            open(unique_file_name, 'w').close()
        await state.finish()
        await call.message.answer("📢 <b>Список ботов очищен!</b>")
    except Exception as e:
        print(f"Error clearing bot list: {e}")
        await call.message.answer("<b>Произошла ошибка при очистке списка ботов.</b>")

@dp.callback_query_handler(text="addd", state="*")
async def ref(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer("📢 <b>Введите Список Юзиков Каждый С Новой Строки:</b>")
    await akasil.sms_text.set()


async def is_bot_alive(bot_username):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://t.me/{bot_username}') as response:
                if response.status == 200:
                    text = await response.text()
                    # Простая проверка на наличие заголовка и описания
                    if 'tgme_page_title' in text and 'tgme_page_description' in text:
                        return True
    except Exception as e:
        print(f"Error checking bot @{bot_username}: {e}")
    return False


@dp.message_handler(state=akasil.sms_text)
async def input_text_for_ad(message: types.Message, state: FSMContext):
    ff = message.text
    ls = ff.strip().split('\n')
    dead_bots = []
    new_bots = []

    for x in ls:
        x = x.strip()
        # Парсинг юзернейма бота
        if x.startswith('https://t.me/'):
            xxx = x.split('https://t.me/')[-1]
        elif x.startswith('@'):
            xxx = x[1:]
        else:
            xxx = x
        xxx = xxx.strip()

        # Проверка доступности бота
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://t.me/{xxx}') as response:
                    if response.status == 200:
                        text = await response.text()
                        if 'fghnfghnfghm' in text and 'srgdfghndfghn' in text:
                            # Бот существует
                            new_bots.append(xxx)
                        else:
                            # Страница не найдена или бот недоступен
                            dead_bots.append(xxx)
                    else:
                        # HTTP статус не 200
                        dead_bots.append(xxx)
        except Exception as e:
            # В случае любой ошибки считаем бота недоступным
            print(f"Error checking bot @{xxx}: {e}")
            dead_bots.append(xxx)

    # Запись новых ботов в файл
    try:
        # Открываем файл в режиме записи, чтобы перезаписать его содержимое
        with open(unique_file_name, "w", encoding='utf-8') as f:
            for bot_username in new_bots:
                f.write(f"{bot_username}\n")
    except Exception as e:
        print(f"Error writing to bot list file: {e}")
        await message.answer("<b>Произошла ошибка при сохранении ботов. Попробуйте еще раз.</b>")
        return

    # Обновление списка botttt с использованием блокировки
    async with botttt_lock:
        botttt.clear()
        botttt.extend(new_bots)

    await state.finish()

    # Формирование сообщения для отправки администратору
    added_count = len(new_bots)
    total_count = len(ls)
    msg = f"📢 <b>Было добавлено {added_count} ботов из {total_count}!</b>"
    if dead_bots:
        dead_bots_list = '\n'.join(dead_bots)
        msg += f"\n\n<b>Неактивные боты:</b>\n{dead_bots_list}"
    await message.answer(msg)

async def nowi(message):
    chat_id = message.chat.id
    if len(botttt) >= 1:
        while True:
            msg = random.choice(botttt)

            # Проверяем доступность бота с новой функцией
            if await is_bot_alive(msg):
                # Бот существует, продолжаем выполнение
                baza.append(chat_id)
                do_spiska = f"{chat_id}:{msg}"
                spisok.append(do_spiska)

                sss = await message.answer(
                    f"<b>✳️ Привет {message.from_user.first_name} ✳️</b>\n\n"
                    f"➖➖➖➖➖➖➖➖➖➖➖\n"
                    f"<b>Вот твой Бот: <a href='http://t.me/{msg}'>@{msg}</a></b>\n\n"
                    f"➖➖➖➖➖➖➖➖➖➖➖\n"
                    f"<b>Если Тот Умрет Вернись Сюда И Получишь Новый:</b>",
                    reply_markup=menu
                )
                await bot.pin_chat_message(chat_id=chat_id, message_id=sss.message_id)
                break
            else:
                # Бот недоступен, удаляем из списка и обновляем файл
                botttt.remove(msg)
                await update_bot_file(botttt)  # Обновляем файл с ботами
    else:
        await message.answer("<b>Боты скоро появятся</b>", reply_markup=menu)

async def starii(message):
    chat_id = message.chat.id
    for x in spisok:
        xx = int(x.split(':')[0])

        if xx == chat_id:
            msg = x.split(":")[1]

            # Проверяем доступность бота с помощью новой функции
            if await is_bot_alive(msg):  # Используем функцию проверки бота
                # Бот доступен, продолжаем выполнение
                ms = msg
                baza.append(chat_id)
                do_spiska = f"{chat_id}:{ms}"
                spisok.append(do_spiska)
                await message.answer(
                    f"<b>✳️ Привет {message.from_user.first_name} ✳️</b>\n\n"
                    f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                    f"<b>Твой Бот: <a href='http://t.me/{ms}'>@{ms}</a> Жив</b>\n\n"
                    f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                    f"<b>Если Тот Умрет Вернись Сюда И Получишь Новый:</b>",
                    reply_markup=menu
                )
                break
            else:
                # Бот недоступен, удаляем из списка spisok и обновляем файл
                spisok.remove(x)  # Удаляем запись из spisok
                async with file_lock:  # Блокируем доступ к файлу
                    with open(unique_file_name, "w", encoding="utf-8") as f:
                        for bot in botttt:
                            f.write(f"{bot}\n")
                
                # Выдаём нового бота
                await nowi(message)

ps = []
@dp.message_handler(text='ℹ️ Получить Бота ℹ️', state="*")
@dp.message_handler(commands=['start'], state="*")
async def show_contact(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    if chat_id in baza:
        task2 = asyncio.create_task(starii(message))
        await task2
    else:
        task1 = asyncio.create_task(nowi(message))
        await task1

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    asyncio.run()
