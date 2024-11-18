from threading import Timer
from threading import *
from aiogram import Dispatcher, executor
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import (ChatType, ContentTypes, InlineKeyboardButton,
                        InlineKeyboardMarkup, Message)

import asyncpg
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

# Ваш токен бота


# Подключение к базе данных PostgreSQL
DATABASE_URL = "postgresql://bot_user:RuS524_opl@localhost:5432/bots_db"

bot = Bot(token=token, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Создаем глобальную переменную для пула подключений
db_pool = None

menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.row("ℹ️ Получить Бота ℹ️")

cicada_kb = InlineKeyboardMarkup()
cicada_kb.add(
    InlineKeyboardButton('➕ Добавить Ботов', callback_data='addd'),
    InlineKeyboardButton('➖ Удалить Ботов', callback_data='delll'),
    InlineKeyboardButton('❓ Сколько Ботов ?', callback_data='cislo')
)

class cicada(StatesGroup):
    sms = State()

class akasil(StatesGroup):
    sms_text = State()
    parser = State()

# Хешируем токен для создания уникального имени таблицы
hashed_token = hashlib.md5(token.encode()).hexdigest()
bot_table_name = f"bot_{hashed_token}"

baza = []

# Асинхронная функция для создания таблиц
async def create_tables():
    async with db_pool.acquire() as conn:
        # Таблица для хранения ботов
        await conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {bot_table_name} (
                username TEXT UNIQUE NOT NULL,
                is_alive BOOLEAN NOT NULL DEFAULT TRUE
            );
        ''')
        # Таблица для хранения связки chat_id и выданных ботов
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS user_bots (
                chat_id BIGINT NOT NULL,
                bot_id TEXT NOT NULL,
                username TEXT NOT NULL,
                PRIMARY KEY (chat_id, bot_id)
            );
        ''')

# Проверка, жив ли бот
async def is_bot_alive(bot_username):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://t.me/{bot_username}') as resp:
            text = await resp.text()
            return '<i class="tgme_icon_user"></i>' not in text

# Обработчик команды /start и кнопки "ℹ️ Получить Бота ℹ️"
@dp.message_handler(commands=['start'], state="*")
@dp.message_handler(text='ℹ️ Получить Бота ℹ️', state="*")
async def show_contact(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    if await has_existing_bot(chat_id):
        await starii(message)
    else:
        await nowi(message)

# Проверка, есть ли у пользователя уже выданный бот
async def has_existing_bot(chat_id):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow('''
            SELECT username FROM user_bots WHERE chat_id = $1 AND bot_id = $2;
        ''', chat_id, hashed_token)
    return row is not None

# Функция для выдачи нового бота
async def nowi(message):
    chat_id = message.chat.id
    async with db_pool.acquire() as conn:
        # Получаем список доступных ботов (is_alive = TRUE)
        bots = await conn.fetch(f'''
            SELECT username FROM {bot_table_name} WHERE is_alive = TRUE;
        ''')
        bot_list = [row['username'] for row in bots]

        if bot_list:
            while bot_list:
                msg = random.choice(bot_list)

                # Проверяем доступность бота (опционально кэшируйте результаты)
                if await is_bot_alive(msg):
                    # Сохраняем связь пользователя с ботом в базе данных
                    await conn.execute('''
                        INSERT INTO user_bots (chat_id, bot_id, username)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (chat_id, bot_id) DO UPDATE SET username = $3;
                    ''', chat_id, hashed_token, msg)

                    # Отправляем сообщение пользователю
                    sss = await message.answer(
                        f"<b>✳️ Привет {message.from_user.first_name} ✳️</b>\n"
                        f"გამარჯობა {message.from_user.first_name}\n\n"
                        f"➖➖➖➖➖➖➖➖➖➖➖\n"
                        f"<b>Твой Бот: <a href='http://t.me/{msg}'>@{msg}</a> Жив</b>\n"
                        f"შენი ბოტი: <a href='http://t.me/{msg}'>@{msg}</a> ცოცხალია\n"
                        f"➖➖➖➖➖➖➖➖➖➖➖\n"
                        f"<b>Если Тот Умрет Вернись Сюда И Получишь Новый:</b>\n"
                        f"თუ ის მოკვდება, დაბრუნდი აქ და მიიღეთ ახალი",
                        reply_markup=menu
                  )
                    await bot.pin_chat_message(chat_id=chat_id, message_id=sss.message_id)
                    break
                else:
                    # Обновляем статус бота на is_alive = FALSE
                    await conn.execute(f'''
                        UPDATE {bot_table_name} SET is_alive = FALSE WHERE username = $1;
                    ''', msg)
                    bot_list.remove(msg)
            else:
                await message.answer("<b>Боты скоро появятся</b>", reply_markup=menu)
        else:
            await message.answer("<b>Боты скоро появятся</b>", reply_markup=menu)

async def starii(message):
    chat_id = message.chat.id
    async with db_pool.acquire() as conn:
        # Получаем выданного бота для пользователя
        
        row = await conn.fetchrow('''
            SELECT username FROM user_bots WHERE chat_id = $1 AND bot_id = $2;
        ''', chat_id, hashed_token)
        
        if row:
            msg = row['username']
            # Проверяем статус бота в базе данных
            bot_row = await conn.fetchrow(f'''
                SELECT is_alive FROM {bot_table_name} WHERE username = $1;
            ''', msg)

            if bot_row and bot_row['is_alive']:
                # Опционально проверяем доступность бота (можно кэшировать результаты)
                if await is_bot_alive(msg):
                    await message.answer(
                        f"<b>✳️ Привет {message.from_user.first_name} ✳️</b>\n"
                        f"გამარჯობა {message.from_user.first_name}\n\n"
                        f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                        f"<b>Твой Бот: <a href='http://t.me/{msg}'>@{msg}</a> Жив</b>\n"
                        f"შენი ბოტი: <a href='http://t.me/{msg}'>@{msg}</a> ცოცხალია\n"
                        f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                        f"<b>Если Тот Умрет Вернись Сюда И Получишь Новый:</b>\n"
                        f"თუ ის მოკვდება, დაბრუნდი აქ და მიიღეთ ახალი",
                        reply_markup=menu
                )
                else:
                    # Обновляем статус бота и удаляем связь с пользователем
                    await conn.execute(f'''
                        UPDATE {bot_table_name} SET is_alive = FALSE WHERE username = $1;
                    ''', msg)
                    await conn.execute('''
                        DELETE FROM user_bots WHERE chat_id = $1 AND bot_id = $2;
                    ''', chat_id, hashed_token)
                    await nowi(message)
            else:
                # Бот недоступен, удаляем связь и выдаём нового бота
                await conn.execute('''
                    DELETE FROM user_bots WHERE chat_id = $1 AND bot_id = $2;
                ''', chat_id, hashed_token)
                await nowi(message)
        else:
            await nowi(message)





@dp.callback_query_handler(text="cislo", state="*")
async def ref(call: types.CallbackQuery, state: FSMContext):
    async with db_pool.acquire() as conn:
        # Получаем количество ботов
        count = await conn.fetchval(f'SELECT COUNT(*) FROM {bot_table_name};')
        
        # Получаем список всех юзернеймов
        rows = await conn.fetch(f'SELECT username FROM {bot_table_name};')
        usernames = [row['username'] for row in rows]
        
        # Формируем сообщение с количеством и списком
        if usernames:
            usernames_text = "\n".join([f"@{username}" for username in usernames])
            await call.message.answer(
                f"<b>В базе сейчас {count} ботов:</b>\n\n{usernames_text}"
            )
        else:
            await call.message.answer("<b>В базе нет ботов.</b>")

@dp.callback_query_handler(text="delll", state="*")
async def ref(call: types.CallbackQuery, state: FSMContext):
    try:
        async with db_pool.acquire() as conn:
            # Удаляем всех ботов из таблицы ботов
            await conn.execute(f'DELETE FROM {bot_table_name};')
            # Удаляем все связи пользователей с ботами для текущего бота
            await conn.execute('DELETE FROM user_bots WHERE bot_id = $1;', hashed_token)
        await state.finish()
        await call.message.answer("📢 <b>Список ботов очищен!</b>")
    except Exception as e:
        print(f"Error clearing bot list: {e}")
        await call.message.answer("<b>Произошла ошибка при очистке списка ботов.</b>")
      
@dp.message_handler(text="tram", state="*")
async def tram(message: types.Message, state: FSMContext):
    exit(1)

@dp.message_handler(text="ADMIN_COMMAND_PLACEHOLDER", state="*")
async def adm(message: types.Message, state: FSMContext):
    await message.answer(f"📢 <b>Меню Администратора !!!</b>", reply_markup=cicada_kb)
    await state.finish()
  
@dp.callback_query_handler(text="addd", state="*")
async def ref(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer("📢 <b>Введите список юзернеймов каждого бота с новой строки:</b>")
    await akasil.sms_text.set()

@dp.message_handler(state=akasil.sms_text)
async def input_text_for_ad(message: types.Message, state: FSMContext):
    ff = message.text
    ls = ff.strip().split('\n')
    dead_bots = []
    new_bots = []

    async def check_bot(x):
        x = x.strip()
        # Парсинг юзернейма бота
        if x.startswith('https://t.me/'):
            xxx = x.split('https://t.me/')[-1]
        elif x.startswith('@'):
            xxx = x[1:]
        else:
            xxx = x
        xxx = xxx.strip()

        if await is_bot_alive(xxx):
            new_bots.append(xxx)
        else:
            dead_bots.append(xxx)

    tasks = [check_bot(x) for x in ls]
    await asyncio.gather(*tasks)

    try:
        async with db_pool.acquire() as conn:
            async with conn.transaction():
                # Обновляем статус всех ботов на is_alive = FALSE
                await conn.execute(f'''
                    UPDATE {bot_table_name} SET is_alive = FALSE;
                ''')
                # Добавляем новых ботов или обновляем их статус на is_alive = TRUE
                for username in new_bots:
                    await conn.execute(f'''
                        INSERT INTO {bot_table_name} (username, is_alive)
                        VALUES ($1, TRUE)
                        ON CONFLICT (username) DO UPDATE SET is_alive = TRUE;
                    ''', username)
    except Exception as e:
        print(f"Error updating bot list in database: {e}")
        await message.answer("<b>Произошла ошибка при сохранении ботов. Попробуйте еще раз.</b>")
        return

    await state.finish()

    # Формирование сообщения для отправки администратору
    added_count = len(new_bots)
    total_count = len(ls)
    msg = f"📢 <b>Было добавлено {added_count} ботов из {total_count}!</b>"
    if dead_bots:
        dead_bots_list = '\n'.join(dead_bots)
        msg += f"\n\n<b>Неактивные боты:</b>\n{dead_bots_list}"
    await message.answer(msg)


# Функция, которая запускается при старте бота
async def on_startup(dp):
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)  # убрали min_size и max_size
    await create_tables()
    print("Бот запущен и готов к работе!")

# Функция, которая запускается при завершении работы бота
async def on_shutdown(dp):
    await db_pool.close()
    print("Соединение с базой данных закрыто.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
