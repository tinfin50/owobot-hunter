import time
import discord
from config import TOKEN, BOT_ID, MIN_DELAY, MAX_DELAY
import random

#TODO: add error handling and proper logging with the logger library

#declare all needed global variables
CHANNEL_ID = None
total_xp = 0
wins = 0
losses = 0
current_message = True
total_hunts = 0

#initialize the discord client
client = discord.Client(
    chunk_guilds_at_startup=False,
    request_guilds=False
)
#create an attribute in the client object to control the main loop
client.running = False

#function to extract the fighter's name from the embed author, if the author is None it returns "No Author", if the name is empty it returns "error fetching name"
def getNameFromAuthor(author) -> str:
    name = author.name.split(" ") if author else "No Author"
    return name[0] if name else "error fetching name"

#function to handle hunt messages, updates the total hunts and total xp accordingly and prints the results
def handleHuntMessage(message):
    global total_xp, total_hunts
    total_hunts += 1
    xp = getXpFromMessage(message.content)
    print(f"hunted successfully! XP gained: {xp} | Total XP: {total_xp} | Total Hunts: {total_hunts}")

#function to send messages to the channel, first tries to get the channel from the client's cache, if it fails it fetches the channel from the API, then sends the message to the channel
async def sendMessage(channel_id : str, content:str):
    channel = client.get_channel(channel_id)
    if channel is None:
        channel = await client.fetch_channel(channel_id)
    await channel.send(content)

#function to parse numbers from strings, used to extract xp values from messages (this avoids errors that come from number like 9,200)
def numberParser(string) -> int:
    string = str(string)
    number = ""
    for char in string:
        if char.isdigit():
            number += char
    return int(number) if number else 0

#function to check if a message is a battle message, checks if the message is sent by the bot, if it contains embeds, and if the embed author name contains "battle!" (which means it's a battle message)
def checkIfBattleMessage(message) -> bool:
    if message.author.bot and message.author.id == BOT_ID and message.channel.id == CHANNEL_ID:
        if message.embeds:
            for embed in message.embeds:
                author_name = embed.author.name.split(" ") if embed.author else "No Author"
                for name in author_name:
                    if name == "battle!":
                        return True
    return False

#function to extract xp gained from battle messages, looks for parts of the message that start with "+" and returns the xp value, if no xp value is found returns 0
def getXpFromFooter(footer) -> int:
    xp = footer.split(" ") if footer else "No Footer"
    for entry in xp:
        if entry.startswith("+"):
            xp = numberParser(entry[1:])  # Remove the "+" prefix and parse the number
            break
    return xp

#function to extract battle result from battle messages, looks for parts of the message that start with "won" or "lost" and returns the result accordingly
def getResultFromFooter(footer) -> str:
    result = footer.split(" ") if footer else "No Footer"
    for entry in result:
        if entry.startswith("won"):
            return "win"
        elif entry.startswith("lost"):
            return "lost"
    return "error fetching result"

#function to extract xp gained from hunt messages, looks for parts of the message that end with "xp**!" and sums up the xp values, also updates the total xp
def getXpFromMessage(message) -> int:
    global total_xp
    xp = 0
    parts = message.split(" ")
    for part in parts:
        if part.endswith("xp**!"):
            xp += numberParser(part[2:-5])  # Remove the "xp**!" suffix and ** prefix  and convert to integer
    total_xp += xp
    return xp

#function to handle messages sent by the bot, checks if the message is a battle message or a hunt message and calls the appropriate handler function
async def handleBotMessage(message):
    #check if the message contains embeds, if it does check if it's a battle message and handle it accordingly, if it doesn't check if it's a hunt message and handle it accordingly
    if message.embeds:
        for embed in message.embeds:
            if checkIfBattleMessage(message):
                handleBattleMessage(embed)
            else:
                print("Not a battle message.")
    #if the message doesn't contain embeds, check if it's a hunt message and handle it accordingly
    elif message.content.startswith("**🌱"):
        handleHuntMessage(message)

def handleBattleMessage(embed):
    global total_xp, wins, losses
    #extract the fighter's name, battle result, and xp gained from the embed message
    fighter = getNameFromAuthor(embed.author)
    result = getResultFromFooter(embed.footer.text)
    xp = getXpFromFooter(embed.footer.text)
    #if the fighter is the bot itself, update the total xp, wins, and losses accordingly and print the results, otherwise just print the battle message details
    if fighter == client.user.display_name:
        print(f"Fighter: {fighter} | Result: {result} | XP gained: {xp}")
        total_xp += numberParser(xp)
        if result == "win":
            wins += 1
        elif result == "lost":
            losses += 1
        print(f"Total XP: {total_xp} | Wins: {wins} | Losses: {losses}")
    else:
        print("battle message not of self: ")
        print(f"Fighter: {fighter} | Result: {result} | XP: {xp}")

#@client.event is a decorator that registers an event handler for a specific event, in this case on_ready and on_message events, the functions defined below these decorators will be called when the respective events occur
@client.event
#simple event handler that prints a message when the bot is ready and logged in
async def on_ready():
    print(f"succesfully logged in as {client.user}")

#event handler that listens for messages, if the message starts with "$start" and is sent by the bot itself, it sets the channel ID and starts the main loop, if the message starts with "$stop" and is sent by the bot itself, it stops the main loop, if the message is sent by the owo bot and is in the correct channel it calls the handleBotMessage function to process the message
async def on_message(message):
    global CHANNEL_ID
    if message.content.startswith("$start") and message.author.id == client.user.id:
        CHANNEL_ID = message.channel.id
        client.running = True
        await message.edit(content="Started main loop.")
        await main()
    if message.content.startswith("$stop") and message.author.id == client.user.id:
        CHANNEL_ID = None
        client.running = False
        await message.edit(content="Stopped main loop.")
    if message.author.bot and message.author.id == BOT_ID and message.channel.id == CHANNEL_ID:
        await handleBotMessage(message)


#main loop of the bot, alternates between sending "owo h" and "owo b" with a randomized delay to simulate hunting and battling
async def main():
    #variable to alternate between sending "owo h" and "owo b"
    global current_message
    while client.running:
        if current_message:
            await sendMessage(CHANNEL_ID, "owo h")
        else:
            await sendMessage(CHANNEL_ID, "owo b")
        
        #alternate the message to be sent in the next iteration
        current_message = not current_message
        time.sleep(random.randint(MIN_DELAY, MAX_DELAY))
        


client.run(TOKEN)


