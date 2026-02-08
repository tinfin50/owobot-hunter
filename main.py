import time
import discord
from config import TOKEN, CHANNEL_ID, BOT_ID, MIN_DELAY, MAX_DELAY
import random


client = discord.Client(
    chunk_guilds_at_startup=False,
    request_guilds=False
)
client.running = False
total_xp = 0
wins = 0
losses = 0
current_message = True
total_catches = 0
common_catches = 0
uncommon_catches = 0
rare_catches = 0
epic_catches = 0
mythic_catches = 0
special_catches = 0
gem_catches = 0
legendary_catches = 0
fabled_catches = 0
glitch_catches = 0
hidden_catches = 0

class Catchmessage:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if value is not 0:
                setattr(self, key, value)

def handleBattleMessage(embed):
    global total_xp, wins, losses
    fighter = getNameFromAuthor(embed.author)
    result = getResultFromFooter(embed.footer.text)
    xp = getXpFromFooter(embed.footer.text)
    if fighter == client.user.display_name:
        print(f"Fighter: {fighter} | Result: {result} | XP: {xp}")
        total_xp += int(xp)
        if result == "win":
            wins += 1
        elif result == "lost":
            losses += 1
        print(f"Total XP: {total_xp} | Wins: {wins} | Losses: {losses}")
    else:
        print("battle message not of self: ")
        print(f"Fighter: {fighter} | Result: {result} | XP: {xp}")

def checkIfBattleMessage(message):
    if message.author.bot and message.author.id == BOT_ID and message.channel.id == CHANNEL_ID:
        if message.embeds:
            for embed in message.embeds:
                author_name = embed.author.name.split(" ") if embed.author else "No Author"
                for name in author_name:
                    if name == "battle!":
                        return True
    return False

def getNameFromAuthor(author):
    name = author.name.split(" ") if author else "No Author"
    return name[0] if name else "error fetching name"

def getXpFromFooter(footer):
    xp = footer.split(" ") if footer else "No Footer"
    for entry in xp:
        if entry.startswith("+"):
            xp = entry[1:]  # Remove the "+" prefix
            break
    return xp

def getResultFromFooter(footer):
    result = footer.split(" ") if footer else "No Footer"
    for entry in result:
        if entry.startswith("won"):
            return "win"
        elif entry.startswith("lost"):
            return "lost"
    return "error fetching result"

async def sendMessage(channel_id : str, content:str):
    channel = client.get_channel(channel_id)
    if channel is None:
        channel = await client.fetch_channel(channel_id)
    await channel.send(content)

async def handleBotMessage(message):
    if message.embeds:
        for embed in message.embeds:
            if checkIfBattleMessage(message):
                handleBattleMessage(embed)
            else:
                print("Not a battle message.")
    elif message.content.startswith("**🌱"):
        print("hunt message caught")

@client.event
async def on_ready():
    print(f"succesfully logged in as {client.user}")

@client.event
async def on_message(message):
    if message.content.startswith("$start") and message.author.id == client.user.id:
        client.running = True
        await message.edit(content="Started main loop.")
        await main()
    if message.content.startswith("$stop") and message.author.id == client.user.id:
        client.running = False
        await message.edit(content="Stopped main loop.")
    if message.author.bot and message.author.id == BOT_ID and message.channel.id == CHANNEL_ID:
        await handleBotMessage(message)



async def main():
    global current_message
    while client.running:
        if current_message:
            await sendMessage(CHANNEL_ID, "owo h")
        else:
            await sendMessage(CHANNEL_ID, "owo b")
        current_message = not current_message
        time.sleep(random.randint(MIN_DELAY, MAX_DELAY))
        


client.run(TOKEN)


