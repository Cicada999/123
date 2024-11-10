from threading import Timer
from threading import *
from aiogram import Dispatcher, executor
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import (ChatType, ContentTypes, InlineKeyboardButton,
                        InlineKeyboardMarkup, Message)

import redis
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
import aioredis
import asyncpg
import asyncio, time, aiohttp
from aiogram.types import User
import time
from threading import Timer
import asyncio
import sys
import re
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, inline_keyboard
import psycopg2


# Настройки базы данных PostgreSQL
DB_NAME = 'bots_db'
DB_USER = 'bot_user'
DB_PASSWORD = 'RuS524_opl'
DB_HOST = 'localhost'
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
REDIS_URL = "redis://localhost:6379/0"

# Настройки Redis
redis_client = aioredis.from_url(REDIS_URL)
botttt_lock = asyncio.Lock()

# Телеграм бота и интерфейсы
menu = ReplyKeyboardMarkup(resize_keyboard=True).row("ℹ️ Получить Бота ℹ️")
cicada_kb = InlineKeyboardMarkup().add(
    InlineKeyboardButton('➕ Добавить Ботов', callback_data='addd'),
    InlineKeyboardButton('➖ Удалить Ботов', callback_data='delll'),
    InlineKeyboardButton('❓ Сколько Ботов ?', callback_data='cislo')
)

# Telegram Bot Token

bot = Bot(token=token, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

class cicada(StatesGroup):
    sms = State()

class akasil(StatesGroup):
    sms_text = State()

# Инициализация подключения
async def init_redis():
    global redis
    redis = await aioredis.from_url(REDIS_URL)

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)

# Создание базы данных для каждого бота
async def create_bot_database(bot_name):
    db_name = f"{bot_name}_db"
    try:
        # Подключение к основной базе данных postgres
        conn = psycopg2.connect(dbname='postgres', user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
        conn.autocommit = True
        cursor = conn.cursor()

        # Проверка существования базы данных
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        db_exists = cursor.fetchone()

        if db_exists:
            print(f"База данных {db_name} уже существует. Работаем с существующей базой.")
        else:
            # Создание базы данных, если её нет
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"База данных {db_name} успешно создана.")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка при создании или подключении к базе данных {db_name}: {e}")

# Функции работы с ботами в PostgreSQL
async def load_bots_from_db():
    global botttt
    async with db_pool.acquire() as conn:
        botttt = [record['username'] for record in await conn.fetch("SELECT username FROM bots WHERE is_active = TRUE;")]

def add_bot_to_db(username):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bots (username, is_active) VALUES (%s, TRUE) ON CONFLICT (username) DO NOTHING;", (username,))
    conn.commit()
    cursor.close()
    conn.close()

# Проверка активности бота
async def is_bot_alive(username):
    r = requests.get(f'https://t.me/{username}')
    return '<i class="tgme_icon_user"></i>' not in r.text

# Загрузка ботов из Redis при старте
async def load_bots_from_cache():
    global botttt
    cached_bots = await redis.lrange("active_bots", 0, -1)
    if cached_bots:
        botttt = [bot.decode("utf-8") for bot in cached_bots]
    else:
        await load_bots_from_db()
        await redis.lpush("active_bots", *botttt)

# Удаление всех ботов
@dp.callback_query_handler(text="delll", state="*")
async def delete_all_bots(call: CallbackQuery, state: FSMContext):
    async with botttt_lock:
        await redis.delete("botttt")
        async with db_pool.acquire() as conn:
            await conn.execute("DELETE FROM bots")
    await call.message.answer("📢 <b>Список ботов очищен!</b>")
    await state.finish()

# Получение количества активных ботов из Redis
@dp.callback_query_handler(text="cislo", state="*")
async def get_bot_count(call: CallbackQuery, state: FSMContext):
    bot_count = await redis.scard("botttt")
    await call.message.answer(f"<b>В Базе Сейчас {bot_count} Ботов</b>")

# Добавление новых ботов
@dp.callback_query_handler(text="addd", state="*")
async def add_bot_handler(call: CallbackQuery, state: FSMContext):
    await call.message.answer("📢 <b>Введите Список Юзиков Каждый С Новой Строки:</b>")
    await akasil.sms_text.set()

@dp.message_handler(state=akasil.sms_text)
async def input_text_for_ad(message: Message, state: FSMContext):
    usernames = message.text.strip().split('\n')
    new_bots, dead_bots = [], []
    for username in usernames:
        username = username.replace("https://t.me/", "").replace("@", "")
        if await is_bot_alive(username):
            add_bot_to_db(username)
            await redis.set(username, "active")
            new_bots.append(username)
        else:
            dead_bots.append(username)

    msg = f"📢 <b>Добавлено {len(new_bots)} ботов.</b>\n"
    if dead_bots:
        msg += f"<b>Неактивные боты:</b>\n" + '\n'.join(dead_bots)
    await message.answer(msg)
    await state.finish()

# Получение активного бота
async def get_active_bot():
    async with db_pool.acquire() as conn:
        bot_usernames = [record['username'] for record in await conn.fetch("SELECT username FROM bots WHERE is_active = TRUE")]
        return random.choice(bot_usernames) if bot_usernames else None

async def nowi(message):
    chat_id = str(message.chat.id)
    bot_username = await get_active_bot()

    if not bot_username:
        await message.answer("<b>Боты скоро появятся</b>", reply_markup=menu)
        return

    # Проверка доступности бота
    if await is_bot_alive(bot_username):
        # Сохранение в Redis
        await redis.set(chat_id, bot_username)
        
        # Сообщение о выдаче бота
        sss = await message.answer(
            f"<b>✳️ Привет {message.from_user.first_name} ✳️</b>\n"
            f"გამარჯობა {message.from_user.first_name}\n\n"
            f"➖➖➖➖➖➖➖➖➖➖➖\n"
            f"<b>Твой Бот: <a href='http://t.me/{bot_username}'>@{bot_username}</a> Жив</b>\n"
            f"შენი ბოტი: <a href='http://t.me/{bot_username}'>@{bot_username}</a> ცოცხალია\n"
            f"➖➖➖➖➖➖➖➖➖➖➖\n"
            f"<b>Если Тот Умрет Вернись Сюда И Получишь Новый:</b>\n"
            f"თუ ის მოკვდება, დაბრუნდი აქ და მიიღეთ ახალი",
            reply_markup=menu
        )
        await bot.pin_chat_message(chat_id=message.chat.id, message_id=sss.message_id)
    else:
        # Обновление статуса бота на неактивный
        await update_bot_status(bot_username, False)
        await nowi(message)

# Функция для повторного получения бота
async def starii(message):
    chat_id = str(message.chat.id)
    bot_username = await redis.get(chat_id)
    
    if bot_username and await is_bot_alive(bot_username.decode()):
        await message.answer(
            f"<b>✳️ Привет {message.from_user.first_name} ✳️</b>\n"
            f"გამარჯობა {message.from_user.first_name}\n\n"
            f"➖➖➖➖➖➖➖➖➖➖➖\n"
            f"<b>Твой Бот: <a href='http://t.me/{bot_username.decode()}'>@{bot_username.decode()}</a> Жив</b>\n"
            f"შენი ბოტი: <a href='http://t.me/{bot_username.decode()}'>@{bot_username.decode()}</a> ცოცხალია\n"
            f"➖➖➖➖➖➖➖➖➖➖➖\n"
            f"<b>Если Тот Умрет Вернись Сюда И Получишь Новый:</b>\n"
            f"თუ ის მოკვდება, დაბრუნდი აქ და მიიღეთ ახალი",
            reply_markup=menu
        )
    else:
        await nowi(message)

# Команда /start и "ℹ️ Получить Бота ℹ️"
@dp.message_handler(commands=["start"])
@dp.message_handler(lambda message: message.text == "ℹ️ Получить Бота ℹ️")
async def show_contact(message: Message, state: FSMContext):
    chat_id = str(message.chat.id)
    if await redis.exists(chat_id):
        await starii(message)
    else:
        await nowi(message)

# Инициализация
async def on_startup(dp):
    bot_info = await bot.get_me()
    await create_bot_database(bot_info.username)
    await init_redis()
    await init_db()
    await load_bots_from_cache()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
