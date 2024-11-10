import asyncio
import random
import hashlib
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import redis
import psycopg2
from psycopg2 import sql

# Настройки базы данных PostgreSQL
DB_NAME = 'bots_db'
DB_USER = 'bot_user'
DB_PASSWORD = 'RuS524_opl'
DB_HOST = 'localhost'

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

bot = Bot(token=token, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

menu = ReplyKeyboardMarkup(resize_keyboard=True).row("ℹ️ Получить Бота ℹ️")

# Подключение к базе данных PostgreSQL
def connect_to_db():
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)

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


@dp.message_handler(text="tram", state="*")
async def tram(message: types.Message, state: FSMContext):
    exit(1)

@dp.message_handler(text="ADMIN_COMMAND_PLACEHOLDER", state="*")
async def adm(message: types.Message, state: FSMContext):
    await message.answer(f"📢 <b>Меню Администратора !!!</b>", reply_markup=cicada_kb)
    await state.finish()



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
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM bots WHERE is_active = TRUE;")
    bots = cursor.fetchall()
    cursor.close()
    conn.close()
    if bots:
        return random.choice(bots)[0]
    return None

# Обработчик получения бота
async def nowi(message: types.Message):
    chat_id = message.chat.id
    while True:
        bot_username = await get_active_bot()
        if not bot_username:
            await message.answer("<b>Нет доступных ботов в данный момент.</b>", reply_markup=menu)
            return

        if await is_bot_alive(bot_username):
            redis_client.set(f"user:{chat_id}:bot", bot_username)
            await message.answer(
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
            break
        else:
            remove_bot_from_db(bot_username)

# Обработчик команды /start
@dp.message_handler(commands=['start'], state="*")
async def show_contact(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    if redis_client.get(f"user:{chat_id}:bot"):
        await message.answer("<b>Уже назначен бот.</b>")
    else:
        await nowi(message)

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)

