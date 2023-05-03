import discord
import mysql.connector
import json
import datetime

intents = discord.Intents.all()
client = discord.Client(intents=intents)

with open("bad_words.json") as file:
    data = json.load(file)
    insults = data["bad_words"]

db = mysql.connector.connect(
    host="",
    user="",
    password="",
    database="",
    port=3306
)

def add_warning(user_id):
    cursor = db.cursor()
    current_time = datetime.datetime.now()
    cursor.execute("INSERT INTO warnings (user_id, created_at) VALUES (%s, %s)", (user_id, current_time))
    db.commit()

def get_warnings_count(user_id):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM warnings WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    return result[0]

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

def reset_warnings(user_id):
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM warnings WHERE user_id={user_id}")
    db.commit()

@client.event
async def on_message(message):
    if message.author.bot:
        return

    for insult in insults:
        if insult.lower() in message.content.lower():
            await message.delete()
            add_warning(message.author.id)
            warnings_count = get_warnings_count(message.author.id)

            embed = discord.Embed(
                title="Warning",
                description=f"{message.author.mention}, your message was deleted due to offensive language.",
                color=discord.Color.red()
            )

            moderation_channel = client.get_channel(1040886998195519540)

            if warnings_count >= 3:
                embed.add_field(name="Ban", value="You have been banned due to receiving 3 warnings for offensive language.")
                dm_channel = await message.author.create_dm()
                dm_success = False

                try:
                    await dm_channel.send(embed=embed)
                    dm_success = True
                except discord.errors.Forbidden:
                    dm_success = False

                reset_warnings(message.author.id)
                await message.author.ban(reason='3 warnings for offensive language')
                ban_embed = discord.Embed(
                    title="User Banned",
                    description=f"{message.author.mention} has been banned due to receiving 3 warnings for offensive language.",
                    color=discord.Color.red()
                )
                ban_embed.add_field(name="DM Sent", value="Yes" if dm_success else "No")
                await moderation_channel.send(embed=ban_embed)
            else:
                embed.add_field(name="Warnings", value=f"You have {warnings_count} warning(s) for offensive language.")
                await message.channel.send(embed=embed)
                warning_embed = discord.Embed(
                    title="User Warning",
                    description=f"{message.author.mention} has received a warning for offensive language.",
                    color=discord.Color.red()
                )
                warning_embed.add_field(name="Warning Count", value=warnings_count)
                await moderation_channel.send(embed=warning_embed)

            break

TOKEN = '' # your token here 
client.run(TOKEN)
