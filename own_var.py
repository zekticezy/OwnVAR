import discord
import random
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

with open('TOKEN.txt', 'r') as f:
    TOKEN = f.read().strip()

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.content.startswith('!own') and message.reference:
        referenced_message = await message.channel.fetch_message(message.reference.message_id)

        guild = message.guild
        member_found = None

        for member in guild.members:
            if (member.name.lower() in referenced_message.content.lower() or
                    (member.nick and member.nick.lower() in referenced_message.content.lower())):
                member_found = member
                break
        
        if member_found:
            await message.channel.send("_OwnVAR is verifying this own..._")
            
            result = random.randint(0, 1)
            
            if result == 1:
                await message.channel.send(f"Own has been accepted. {member_found.mention} has been owned.")
                await message.channel.send("https://tenor.com/bG2aC.gif")
            else:
                await message.channel.send(f"Own has been rejected. {member_found.mention} was not owned.")
                await message.channel.send("https://tenor.com/bd3Tv.gif")
        else:
            await message.channel.send("No matching member found in the referenced message.")
    
    await bot.process_commands(message)

bot.run(TOKEN)
