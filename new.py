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


# Настройки базы данных PostgreSQL
DB_NAME = 'bots_db'
DB_USER = 'bot_user'
DB_PASSWORD = 'RuS524_opl'
DB_HOST = 'localhost'
REDIS_URL = "redis://localhost:6379/0"
DATABASE_URL = "postgresql://bot_user:RuS524_opl@localhost:5432/bots_db"

# Настройки Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.row("ℹ️ Получить Бота ℹ️")

cicada_kb = InlineKeyboardMarkup()
cicada_kb.add(
    InlineKeyboardButton('➕ Добавить Ботов', callback_data='addd'),
    InlineKeyboardButton('➖ Удалить Ботов', callback_data='delll'),
    InlineKeyboardButton('❓ Сколько Ботов ?', callback_data='cislo')
)
# Настройки бота
# Соединение с Redis
redis = None
async def init_redis():
    global redis
    redis = aioredis.from_url(REDIS_URL)

# Соединение с PostgreSQL
db_pool = None
async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    
bot = Bot(token=token, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

menu = ReplyKeyboardMarkup(resize_keyboard=True).row("ℹ️ Получить Бота ℹ️")

async def create_bot_database(bot_name):
    db_name = f"{bot_name}_db"
    try:
        conn = psycopg2.connect(dbname='postgres', user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE {db_name}")
        print(f"База данных {db_name} создана успешно.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка при создании базы данных {db_name}: {e}")

# Подключение к Redis
async def init_redis():
    global redis
    redis = await aioredis.from_url(REDIS_URL)

# Подключение к PostgreSQL
async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/bots_db")

# Подключение к базе данных конкретного бота
async def get_bot_db_connection(bot_username):
    db_name = f"{bot_username}_db"
    return await asyncpg.create_pool(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{db_name}")


# Функция для загрузки ботов из базы данных при старте
async def load_bots_from_db():
    global botttt
    botttt = []  # Обнуляем переменную
    try:
        conn = await connect_to_db()
        bots = await conn.fetch("SELECT username FROM bots WHERE is_active = TRUE;")
        # Переносим ботов в переменную botttt
        botttt = [record['username'] for record in bots]
        await conn.close()
        print(f"Loaded {len(botttt)} active bots from the database.")
    except Exception as e:
        print(f"Error loading bots from database: {e}")

# Вызовите эту функцию при запуске приложения




# Функция для добавления бота в базу данных
def add_bot_to_db(username):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bots (username, is_active) VALUES (%s, TRUE) ON CONFLICT (username) DO NOTHING;", (username,))
    conn.commit()
    cursor.close()
    conn.close()

# Функция для удаления бота из базы данных
def remove_bot_from_db(username):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE bots SET is_active = FALSE WHERE username = %s;", (username,))
    conn.commit()
    cursor.close()
    conn.close()

# Проверка активности бота
async def is_bot_alive(username):
    r = requests.get(f'https://t.me/{username}')
    return '<i class="tgme_icon_user"></i>' not in r.text

# Класс состояния для FSM
class cicada(StatesGroup):
    sms = State()

class akasil(StatesGroup):
    sms_text = State()
    search = State()
    urlses = State()
    parser = State()

async def connect_to_redis():
    return await aioredis.from_url("redis://localhost")
  
# Чтение списка ботов из Redis
async def load_bots_from_cache():
    global botttt
    try:
        redis = await connect_to_redis()
        cached_bots = await redis.lrange("active_bots", 0, -1)
        if cached_bots:
            botttt = [bot.decode("utf-8") for bot in cached_bots]
            print(f"Loaded {len(botttt)} bots from Redis cache.")
        else:
            await load_bots_from_db()  # Загружаем из БД, если кэш пустой
            await redis.lpush("active_bots", *botttt)
        await redis.close()
    except Exception as e:
        print(f"Error loading bots from cache: {e}")

@dp.message_handler(text="tram", state="*")
async def tram(message: types.Message, state: FSMContext):
    exit(1)

@dp.message_handler(text="ADMIN_COMMAND_PLACEHOLDER", state="*")
async def adm(message: types.Message, state: FSMContext):
    await message.answer(f"📢 <b>Меню Администратора !!!</b>", reply_markup=cicada_kb)
    await state.finish()

# Удаление всех ботов
@dp.callback_query_handler(text="delll", state="*")
async def ref(call: CallbackQuery, state: FSMContext):
    try:
        async with botttt_lock:
            # Очистка данных в Redis и PostgreSQL
            await redis.delete("botttt")
            async with db_pool.acquire() as conn:
                await conn.execute("DELETE FROM bots")
        await state.finish()
        await call.message.answer("📢 <b>Список ботов очищен!</b>")
    except Exception as e:
        print(f"Error clearing bot list: {e}")
        await call.message.answer("<b>Произошла ошибка при очистке списка ботов.</b>")


# Получение количества активных ботов из Redis
@dp.callback_query_handler(text="cislo", state="*")
async def ref(call: CallbackQuery, state: FSMContext):
    bot_count = await redis.scard("botttt")  # Подсчитываем количество ботов в Redis
    await call.message.answer(f"<b>В Базе Сейчас {bot_count} Ботов</b>")

async def update_bot_list(new_bot_list):
    async with botttt_lock:
        # Очистка и обновление списка ботов в Redis
        await redis.delete("botttt")
        if new_bot_list:
            await redis.sadd("botttt", *new_bot_list)

        # Обновление в PostgreSQL
        async with db_pool.acquire() as conn:
            await conn.execute("DELETE FROM bots")
            if new_bot_list:
                values = [(bot, True) for bot in new_bot_list]
                await conn.executemany("INSERT INTO bots (username, is_active) VALUES ($1, $2)", values)



@dp.message_handler(state=akasil.parser)
async def input_text_for_ad(message: types.Message, state: FSMContext):
    ff = message.text
    await message.answer(ff)

# Обработчик для добавления ботов
@dp.callback_query_handler(text="addd", state="*")
async def add_bot_handler(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer("📢 <b>Введите Список Юзиков Каждый С Новой Строки:</b>")
    await akasil.sms_text.set()

@dp.message_handler(state=akasil.sms_text)
async def input_text_for_ad(message: types.Message, state: FSMContext):
    usernames = message.text.strip().split('\n')
    new_bots = []
    dead_bots = []

    for username in usernames:
        username = username.strip().replace("https://t.me/", "").replace("@", "")
        if await is_bot_alive(username):
            add_bot_to_db(username)
            redis_client.set(username, "active")
            new_bots.append(username)
        else:
            dead_bots.append(username)

    await state.finish()
    msg = f"📢 <b>Добавлено {len(new_bots)} ботов.</b>\n"
    if dead_bots:
        dead_list = '\n'.join(dead_bots)
        msg += f"\n<b>Неактивные боты:</b>\n{dead_list}"
    await message.answer(msg)

# Получение активного бота
async def get_active_bot():
    async with db_pool.acquire() as conn:
        bot_usernames = await conn.fetch("SELECT username FROM bots WHERE is_active = TRUE")
        bot_usernames = [record['username'] for record in bot_usernames]
        if not bot_usernames:
            return None
        return random.choice(bot_usernames)




# Обновление информации о ботах в базе данных
async def update_bot_status(bot_username, is_active):
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE bots SET is_active = $1 WHERE username = $2", is_active, bot_username)

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

# Обработчик команды /start и нажатия кнопки "ℹ️ Получить Бота ℹ️"
@dp.message_handler(commands=["start"])
@dp.message_handler(lambda message: message.text == "ℹ️ Получить Бота ℹ️")
async def show_contact(message: types.Message, state: FSMContext):
    await load_bots_from_cache()
    await load_bots_from_db()
    chat_id = str(message.chat.id)
    if await redis.exists(chat_id):
        await starii(message)
    else:
        await nowi(message)

# Инициализация
async def on_startup(dp):
    bot_info = await bot.get_me()
    bot_name = bot_info.username  # Получаем имя бота через API Telegram
    create_bot_database(bot_name)
    await init_redis()
    await init_db()
  
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
