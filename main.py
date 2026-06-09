import discord # pyright: ignore [reportMissingImports]
from discord.ext import commands, tasks # pyright: ignore [reportMissingImports]
from discord import app_commands # pyright: ignore [reportMissingImports]
import logging
import os
import asyncio
from dotenv import load_dotenv # pyrefly: ignore [missing-import]

load_dotenv() #Carregando .env

logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix="!!",intents=discord.Intents.all(),application_id=int(os.getenv("BOT_ID")))

class SubButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
        self.timeout=600

        botaourl = discord.ui.Button(label="DuneGG",url="https://www.youtube.com/@DuneGG?sub_confirmation=1")
        self.add_item(botaourl)

@bot.event
async def on_ready(): 
    print("Estou online!")

@bot.command()
@commands.is_owner() 
async def sync(ctx,guild=None):
    if guild == None:
        await bot.tree.sync()
    else:
        await bot.tree.sync(guild=discord.Object(id=int(guild)))
    await ctx.send("**Sincronizado!** O projeto base foi feito por DuneDiscord!",view=SubButton())

async def main():
    async with bot:
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')

        
        TOKEN = os.getenv("DISCORD_TOKEN")
        await bot.start(TOKEN)

asyncio.run(main())

