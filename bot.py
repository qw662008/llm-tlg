import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
import aiohttp

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token='7709642419:AAEchdrcFa9JV9iDbONqNh-sUoLYLBYh-r0')
dp = Dispatcher()

# URL для LM Studio API
LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"

# Создание клавиатуры
def get_keyboard():
    kb = [[KeyboardButton(text="Start"), KeyboardButton(text="Help")]]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    return keyboard

# Функция для отправки запросов к LM Studio API
async def get_llm_response(message: str) -> str:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                LM_STUDIO_URL,
                json={
                    "messages": [{"role": "user", "content": message}],
                    "model": "meta-llama-3.1-8b-instruct",
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content']
                else:
                    return "Извините, произошла ошибка при обработке запроса."
        except Exception as e:
            return f"Ошибка при подключении к LM Studio API: {str(e)}"

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Здравствуйте, я бот-помощник PM",
        reply_markup=get_keyboard()
    )

# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = """
    Доступные команды:
    /start - Начать работу с ботом
    /help - Показать справку
    
    Вы также можете отправить любой текст, и я постараюсь помочь вам с ответом.
    """
    await message.answer(help_text, reply_markup=get_keyboard())

# Обработчик текстовых сообщений
@dp.message()
async def handle_text(message: types.Message):
    if message.text == "Start":
        await cmd_start(message)
    elif message.text == "Help":
        await cmd_help(message)
    else:
        # Отправляем индикатор набора текста
        await message.answer("Обрабатываю ваш запрос...")
        # Получаем ответ от LM Studio API
        response = await get_llm_response(message.text)
        # Отправляем ответ пользователю
        await message.answer(response)

# Функция запуска бота
async def main():
    logging.info("Бот запущен...")
    await dp.start_polling(bot)

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
