from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import aiohttp
import base64
import io

API_TOKEN = 'ваш токен'
API_ENDPOINT = 'https://quotes.fl1yd.su/generate'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def get_user_avatar(user_id):
    user_photos = await bot.get_user_profile_photos(user_id)
    if user_photos.photos:
        photo = user_photos.photos[0][0]
        file_id = photo.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        avatar_bytes = await bot.download_file(file_path)
        return avatar_bytes
    return None

async def api_request(data):
    async with aiohttp.ClientSession() as session:
        async with session.post(API_ENDPOINT, json=data) as response:
            return await response.read()

@dp.message_handler(commands=['q'])
async def create_quote(message: types.Message):
    if not message.reply_to_message:
        await message.reply("Ответьте на сообщение, чтобы создать цитату.")
        return

    # Получаем аватар пользователя
    avatar = await get_user_avatar(message.from_user.id)
    # Преобразуем объект BytesIO в байты
    avatar_bytes = avatar.read() if avatar else None
    # Кодируем байты в base64
    avatar_base64 = base64.b64encode(avatar_bytes).decode() if avatar_bytes else None

    
    payload = {
        'messages': [
            {
                'text': message.reply_to_message.text,
                'media': None,
                'entities': [],
                'author': {
                    'id': message.from_user.id,
                    'name': message.from_user.full_name,
                    'avatar': avatar_base64,
                    'rank': '',
                    'via_bot': None,
                },
                'reply': {
                    'id': None,
                    'name': None,
                    'text': None,
                },
            }
        ],
        'quote_color': '#162330',
        'text_color': '#fff',
    }

    quote_data = await api_request(payload)
    if not quote_data:
        await message.reply("Произошла ошибка при запросе к API.")
        return

    # Создаем объект BytesIO из полученных данных
    quote = io.BytesIO(quote_data)
    quote.name = "quote.webp"
    # Отправляем стикер в чат
    await bot.send_sticker(chat_id=message.chat.id, sticker=quote)

if __name__ == '__main__':
    executor.start_polling(dp)
    
