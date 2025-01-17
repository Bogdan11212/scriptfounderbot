import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Включаем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ваш токен, полученный от @BotFather
TELEGRAM_TOKEN = 'tokentipopon:-'

# Создаем экземпляры бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Создаем клавиатуру
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("Показать последние скрипты"))
keyboard.add(KeyboardButton("Поиск скрипта по названию"))
keyboard.add(KeyboardButton("Показать трендовые скрипты"))  # Новая кнопка

# Функция для обработки команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply('Привет! Выберите действие:', reply_markup=keyboard)

# Функция для показа последних скриптов
@dp.message_handler(lambda message: message.text == "Показать последние скрипты")
async def show_latest_scripts(message: types.Message):
    response = requests.get("https://rscripts.net/api/v2/scripts?page=1&orderBy=date&sort=desc")
    
    if response.status_code == 200:
        scripts_data = response.json().get('scripts', [])
        if not scripts_data:
            await message.reply('Нет доступных скриптов.')
            return
        
        message_text = "Вот последние скрипты:\n\n"
        for script in scripts_data:
            title = script.get('title', 'Без названия')
            description = script.get('description', 'Нет описания')
            creator = script.get('user', {}).get('username', script.get('creator', 'Неизвестный'))
            message_text += f"📝 {title}\n{description}\n👤 Создатель: {creator}\n\n"
        
        await message.reply(message_text)
    else:
        await message.reply('Ошибка при получении скриптов.')

# Функция для поиска скрипта по названию
@dp.message_handler(lambda message: message.text == "Поиск скрипта по названию")
async def search_script(message: types.Message):
    await message.reply('Введите название игры или ссылку на нее:')

@dp.message_handler()
async def handle_search(message: types.Message):
    query = message.text
    response = requests.get("https://rscripts.net/api/v2/scripts?page=1&orderBy=date&sort=desc")
    
    if response.status_code == 200:
        scripts_data = response.json().get('scripts', [])
        found_scripts = [script for script in scripts_data if query.lower() in script.get('title', '').lower()]
        
        if not found_scripts:
            await message.reply('Скрипты не найдены.')
            return
        
        message_text = "Найденные скрипты:\n\n"
        for script in found_scripts:
            title = script.get('title', 'Без названия')
            description = script.get('description', 'Нет описания')
            creator = script.get('user', {}).get('username', script.get('creator', 'Неизвестный'))
            message_text += f"📝 {title}\n{description}\n👤 Создатель: {creator}\n\n"
        
        await message.reply(message_text)
    else:
        await message.reply('Ошибка при получении скриптов.')

# Функция для показа трендовых скриптов
@dp.message_handler(lambda message: message.text == "Показать трендовые скрипты")
async def show_trending_scripts(message: types.Message):
    response = requests.get("https://rscripts.net/api/v2/trending")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            trending_scripts = data['success']
            if not trending_scripts:
                await message.reply('Нет трендовых скриптов.')
                return
            
            message_text = "Вот трендовые скрипты:\n\n"
            for script in trending_scripts:
                title = script.get('title', 'Без названия')
                description = script.get('description', 'Нет описания')
                creator = script.get('user', {}).get('username', script.get('creator', 'Неизвестный'))
                message_text += f"📝 {title}\n{description}\n👤 Создатель: {creator}\n\n"
            
            await message.reply(message_text)
        else:
            await message.reply(f"Ошибка: {data.get('error', 'Неизвестная ошибка')}")
    else:
        await message.reply('Ошибка при получении трендовых скриптов.')

# Функция для обработки команды /script
@dp.message_handler(commands=['script'])
async def get_script(message: types.Message):
    # Извлекаем ID из сообщения
    command_parts = message.text.split()
    
    if len(command_parts) != 2:
        await message.reply("Пожалуйста, используйте формат: /script <ID>")
        return
    
    script_id = command_parts[1]
    
    # Выполняем запрос к API для получения конкретного скрипта
    response = requests.get(f"https://rscripts.net/api/v2/script?id={script_id}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            script = data['success']
            title = script.get('title', 'Без названия')
            description = script.get('description', 'Нет описания')
            creator = script.get('user', {}).get('username', script.get('creator', 'Неизвестный'))
            
            message_text = f"📝 {title}\n{description}\n👤 Создатель: {creator}"
            await message.reply(message_text)
        else:
            await message.reply(f"Ошибка: {data.get('error', 'Неизвестная ошибка')}")
    else:
        await message.reply('Ошибка при получении скрипта.')

if __name__ == '__main__':
    # Запускаем бота
    executor.start_polling(dp, skip_updates=True)
