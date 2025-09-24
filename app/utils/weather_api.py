import aiohttp
import asyncio
from config import OPENWEATHERMAP_API_KEY

async def get_temp_async(session, city, api_key):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    async with session.get(url) as response:
        data = await response.json()
        if response.status == 401:
            raise ValueError(data.get('message'))
        elif response.status != 200:
            raise ValueError(f"Ошибка API ({response.status}): {data.get('message', 'Неизвестная ошибка')}")
        return data['main']['temp']
    
async def fetch_temperature(city, api_key=OPENWEATHERMAP_API_KEY):
    async with aiohttp.ClientSession() as session:
        return await get_temp_async(session, city, api_key)