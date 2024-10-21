import discord
import random
from discord.ext import commands

# Read the token from TOKEN.txt
with open('TOKEN.txt', 'r') as f:
    TOKEN = f.read().strip()

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.content.startswith('!own') and message.reference:
        referenced_message = await message.channel.fetch_message(message.reference.message_id)
        owner = message.author.mention
        user_to_verify = referenced_message.author.mention
        
        await message.channel.send("_OwnVAR is verifying this own..._")
        
        result = random.randint(0, 1)
        
        if result == 1:
            await message.channel.send(f"Own has been accepted. {user_to_verify} has been owned.")
        else:
            await message.channel.send(f"Own has been rejected. {user_to_verify} was not owned.")
    
    await bot.process_commands(message)

bot.run(TOKEN)
