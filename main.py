import discord
from discord.ext import tasks
import aiohttp
import json
import asyncio

TOKEN = 'Discord-token'
CHANNEL_ID = id-channel  # ID канала для отправки информации
MESSAGE_ID = id-message  # ID сообщения которое нужно редактировать
SERVER_IP = 'your-ip'  # IP адрес вашего сервера
SERVER_PORT = 27015  # Порт сервера (по умолчанию 27015)

class GModBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.status_message = None
        
    async def setup_hook(self):
        self.check_server.start()

    async def on_ready(self):
        print(f'Бот {self.user} запущен!')
        channel = self.get_channel(CHANNEL_ID)
        try:
            self.status_message = await channel.fetch_message(MESSAGE_ID)
        except discord.NotFound:
            print("Сообщение не найдено!")
            return

    async def fetch_server_info(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://api.steampowered.com/IGameServersService/GetServerList/v1/?filter=addr\\{SERVER_IP}:{SERVER_PORT}&key=yourapisteam') as response:
                    data = await response.json()
                    if 'response' in data and 'servers' in data['response']:
                        server = data['response']['servers'][0]
                        return {
                            'name': server['name'],
                            'players': f"{server['players']}/{server['max_players']}",
                            'map': server['map'],
                            'status': 'Онлайн'
                        }
        except Exception as e:
            print(f'Ошибка при получении информации: {e}')
        return {
            'name': 'Нет данных',
            'players': '0/0',
            'map': 'Неизвестно',
            'status': 'Оффлайн'
        }

    @tasks.loop(seconds=5)  # Изменено с minutes=2 на seconds=5
    async def check_server(self):
        if self.status_message:
            info = await self.fetch_server_info()
            
            # Обновляем статус бота
            activity = discord.Game(name=f"Онлайн: {info['players']}")
            await self.change_presence(activity=activity)
            
            embed = discord.Embed(
                title='Статус сервера Garry\'s Mod',
                color=discord.Color.green() if info['status'] == 'Онлайн' else discord.Color.red()
            )
            embed.add_field(name='Название', value=info['name'], inline=False)
            embed.add_field(name='Статус', value=info['status'], inline=True)
            embed.add_field(name='Игроки', value=info['players'], inline=True)
            embed.add_field(name='Карта', value=info['map'], inline=True)
            
            await self.status_message.edit(embed=embed)

async def main():
    client = GModBot()
    await client.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
