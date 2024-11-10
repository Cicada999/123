import asyncio
import hashlib
import random
import re

import aiohttp
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           ReplyKeyboardMarkup)
from aiogram.utils.executor import start_polling

# Ваш токен бота
token = 'YOUR_BOT_TOKEN'

# Подключение к базе данных PostgreSQL
DATABASE_URL = 'postgresql://user:password@localhost:5432/database_name'

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
                username TEXT UNIQUE NOT NULL
            );
        ''')
        # Таблица для хранения связки chat_id и выданных ботов
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS spisok (
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
            SELECT username FROM spisok WHERE chat_id = $1 AND bot_id = $2;
        ''', chat_id, hashed_token)
    return row is not None

# Функция для выдачи нового бота
async def nowi(message):
    chat_id = message.chat.id
    async with db_pool.acquire() as conn:
        # Получаем список ботов из базы данных
        bots = await conn.fetch(f'SELECT username FROM {bot_table_name};')
        bot_list = [row['username'] for row in bots]

    if bot_list:
        while bot_list:
            msg = random.choice(bot_list)

            if await is_bot_alive(msg):
                baza.append(chat_id)

                # Сохраняем в базу данных
                async with db_pool.acquire() as conn:
                    await conn.execute('''
                        INSERT INTO spisok (chat_id, bot_id, username)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (chat_id, bot_id) DO UPDATE SET username = $3;
                    ''', chat_id, hashed_token, msg)

                sss = await message.answer(
                    f"<b>✳️ Привет {message.from_user.first_name} ✳️</b>\n"
                    f"➖➖➖➖➖➖➖➖➖➖➖\n"
                    f"<b>Твой Бот: <a href='http://t.me/{msg}'>@{msg}</a> жив</b>\n"
                    f"➖➖➖➖➖➖➖➖➖➖➖\n"
                    f"<b>Если тот умрет, вернись сюда и получишь новый</b>",
                      reply_markup=menu
                  )
                await bot.pin_chat_message(chat_id=chat_id, message_id=sss.message_id)
                break
            else:
                # Удаляем бота из базы данных
                async with db_pool.acquire() as conn:
                    await conn.execute(f'''
                        DELETE FROM {bot_table_name} WHERE username = $1;
                    ''', msg)
                bot_list.remove(msg)
        else:
            await message.answer("<b>Боты скоро появятся</b>", reply_markup=menu)
    else:
        await message.answer("<b>Боты скоро появятся</b>", reply_markup=menu)

# Функция для выдачи ранее выданного бота
async def starii(message):
    chat_id = message.chat.id
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow('''
            SELECT username FROM spisok WHERE chat_id = $1 AND bot_id = $2;
        ''', chat_id, hashed_token)
    if row:
        msg = row['username']
        if await is_bot_alive(msg):
            await message.answer(
                f"<b>✳️ Привет {message.from_user.first_name} ✳️</b>\n"
                f"➖➖➖➖➖➖➖➖➖➖➖\n"
                f"<b>Твой Бот: <a href='http://t.me/{msg}'>@{msg}</a> жив</b>\n"
                f"➖➖➖➖➖➖➖➖➖➖➖\n"
                f"<b>Если тот умрет, вернись сюда и получишь новый</b>",
                reply_markup=menu
            )
        else:
            # Удаляем запись и выдаем нового бота
            async with db_pool.acquire() as conn:
                await conn.execute('''
                    DELETE FROM spisok WHERE chat_id = $1 AND bot_id = $2;
                ''', chat_id, hashed_token)
            await nowi(message)
    else:
        await nowi(message)

# Администраторские команды
@dp.message_handler(commands=['admin'], state="*")
async def adm(message: types.Message, state: FSMContext):
    await message.answer(f"📢 <b>Меню Администратора !!!</b>", reply_markup=cicada_kb)
    await state.finish()

@dp.callback_query_handler(text="cislo", state="*")
async def ref(call: types.CallbackQuery, state: FSMContext):
    async with db_pool.acquire() as conn:
        count = await conn.fetchval(f'SELECT COUNT(*) FROM {bot_table_name};')
    await call.message.answer(f"<b>В базе сейчас {count} ботов</b>")

@dp.callback_query_handler(text="delll", state="*")
async def ref(call: types.CallbackQuery, state: FSMContext):
    try:
        async with db_pool.acquire() as conn:
            await conn.execute(f'DELETE FROM {bot_table_name};')
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

        if await is_bot_alive(xxx):
            new_bots.append(xxx)
        else:
            dead_bots.append(xxx)
  
    # Обновление базы данных
    try:
        async with db_pool.acquire() as conn:
            # Удаляем всех ботов из таблицы
            await conn.execute(f'DELETE FROM {bot_table_name};')
            # Добавляем новых ботов
            for username in new_bots:
                await conn.execute(f'''
                    INSERT INTO {bot_table_name} (username)
                    VALUES ($1)
                    ON CONFLICT (username) DO NOTHING;
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
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    await create_tables()
    print("Бот запущен и готов к работе!")

# Функция, которая запускается при завершении работы бота
async def on_shutdown(dp):
    await db_pool.close()
    print("Соединение с базой данных закрыто.")

if __name__ == '__main__':
    start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
