import discord
import random
import json
import os
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

with open('TOKEN.txt', 'r') as f:
    TOKEN = f.read().strip()

bot = commands.Bot(command_prefix='!', intents=intents)

with open('members.json', 'r') as f:
    members_data = json.load(f)["members"]

stats_file = 'stats.json'

if not os.path.exists(stats_file):
    with open(stats_file, 'w') as f:
        json.dump({}, f)

def l_variant(name):
    if name:
        return 'l' + name[1:]
    return name

def find_member_in_message(message_content):
    message_content = message_content.lower()
    for member in members_data:
        names_to_check = [member["display_name"]] + member["nicknames"] + [
            l_variant(member["display_name"])
        ] + [l_variant(nick) for nick in member["nicknames"]]
        
        if any(name.lower() in message_content for name in names_to_check):
            return member
    return None

def load_stats():
    with open(stats_file, 'r') as f:
        return json.load(f)

def save_stats(stats):
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=4)

def update_stats(owner_id, owned_id):
    stats = load_stats()
    
    if str(owner_id) not in stats:
        stats[str(owner_id)] = {"owns": 0, "times_owned": 0}
    if str(owned_id) not in stats:
        stats[str(owned_id)] = {"owns": 0, "times_owned": 0}

    stats[str(owner_id)]["owns"] += 1
    stats[str(owned_id)]["times_owned"] += 1

    save_stats(stats)

def reset_user_stats(user_id):
    stats = load_stats()
    if str(user_id) in stats:
        del stats[str(user_id)]
        save_stats(stats)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Successfully synced {len(synced)} commands.')
    except Exception as e:
        print(f'Error syncing commands: {e}')

@bot.tree.command(name="sync", description="Manually sync all slash commands.")
async def sync(interaction: discord.Interaction):
    try:
        synced = await bot.tree.sync()
        await interaction.response.send_message(f"Synced {len(synced)} commands.")
    except Exception as e:
        await interaction.response.send_message(f"Error syncing commands: {e}")

@bot.tree.context_menu(name="Own Someone")
async def own(interaction: discord.Interaction, message: discord.Message):
    member_found = None

    if message.mentions:
        member_found = {
            "user_id": str(message.mentions[0].id),
            "display_name": message.mentions[0].name
        }
    else:
        member_found = find_member_in_message(message.content)

    if member_found:
        await interaction.response.send_message("_OwnVAR is verifying this own..._")
        
        result = random.randint(0, 1)
        verdict = "accepted" if result == 1 else "rejected"

        if result == 1:
            await interaction.followup.send(f"**Own has been {verdict}.** <@{member_found['user_id']}> has been owned by {message.author.mention}.")
            update_stats(message.author.id, member_found['user_id'])
        else:
            await interaction.followup.send(f"**Own has been {verdict}.** <@{member_found['user_id']}> was not owned by {message.author.mention}.")
    else:
        await interaction.response.send_message("No matching member found in the referenced message.")

@bot.tree.context_menu(name="Force Accept Own")
async def force_accept_own(interaction: discord.Interaction, message: discord.Message):
    if interaction.user.id != 495635279387033603:
        return await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

    if message.mentions:
        target = message.mentions[0]
        owner = interaction.user

        update_stats(owner.id, target.id)
        await interaction.response.send_message(f"**Forced own accepted.** <@{target.id}> has been owned by <@{owner.id}>.")
    else:
        await interaction.response.send_message("No member mentioned in the message.")

@bot.tree.context_menu(name="Force Reject Own")
async def force_reject_own(interaction: discord.Interaction, message: discord.Message):
    if interaction.user.id != 495635279387033603:
        return await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

    if message.mentions:
        target = message.mentions[0]
        owner = interaction.user

        await interaction.response.send_message(f"**Forced own rejected.** <@{target.id}> was not owned by <@{owner.id}>.")
    else:
        await interaction.response.send_message("No member mentioned in the message.")

@bot.tree.command(name="stats", description="View own or another member's stats")
async def stats(interaction: discord.Interaction, member: discord.Member = None):
    if member is None:
        member = interaction.user

    stats = load_stats()
    member_id = str(member.id)

    if member_id in stats:
        owns = stats[member_id]["owns"]
        times_owned = stats[member_id]["times_owned"]
    else:
        owns = 0
        times_owned = 0

    leaderboard = sorted(stats.items(), key=lambda x: x[1]['owns'], reverse=True)
    position = next((i + 1 for i, stat in enumerate(leaderboard) if stat[0] == member_id), "N/A")

    await interaction.response.send_message(f"**{member.display_name}'s Owns**\n"
                                            f"Number of owns: {owns}\n"
                                            f"Number of times owned: {times_owned}\n"
                                            f"Spot on own leaderboard: #{position}")

@bot.tree.command(name="ownstats", description="View your own stats")
async def ownstats(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_stats = load_stats().get(user_id)

    if user_stats:
        await interaction.response.send_message(f"**{interaction.user.name}'s Own Stats**\n"
                                                f"Number of owns: {user_stats['owns']}\n"
                                                f"Number of times owned: {user_stats['times_owned']}")
    else:
        await interaction.response.send_message("No stats found for you. You may not have owned anyone yet.")

@bot.tree.command(name="ownboard", description="View the server's own leaderboard")
async def ownboard(interaction: discord.Interaction):
    stats = load_stats()
    leaderboard = []

    for user_id, stat in stats.items():
        owns = stat.get('owns', 0)
        leaderboard.append((user_id, owns))

    leaderboard.sort(key=lambda x: x[1], reverse=True)

    message = "**purple nation Own Leaderboard**\n"
    for i, (user_id, owns) in enumerate(leaderboard[:10], start=1):
        user = await bot.fetch_user(int(user_id))
        message += f"{i}. **{user.display_name}** ({owns} owns)\n"

    if leaderboard:
        top_user_id = leaderboard[0][0]
        top_user = await bot.fetch_user(int(top_user_id))
        message += f"\n🏆🏆***{top_user.display_name} is the owner of the server!***🏆🏆"

    await interaction.response.send_message(message)

@bot.tree.command(name="resetstats", description="Reset a member's stats")
async def resetstats(interaction: discord.Interaction, member: discord.Member):
    if interaction.user.id != 495635279387033603:
        return await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

    reset_user_stats(member.id)
    await interaction.response.send_message(f"**{member.display_name}'s stats have been reset.**")

    try:
        dm_message = (f"Hey {member.display_name},\n\n"
                      "This is an automated message from OwnVAR. Your stats have been reset by zekkie, "
                      "possibly due to abusing the bot.\n"
                      "Please refrain from doing anything like that in the future. Not that I care, "
                      "it's just tiring to reset your stats.\n\n"
                      "Behave.\n- OwnVAR Developer")
        await member.send(dm_message)
    except discord.Forbidden:
        await interaction.followup.send(f"Could not send a DM to {member.display_name}. They might have DMs disabled.")

bot.run(TOKEN)
