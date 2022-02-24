import discord, os, json, asyncio
from discord import Embed
from dotenv import load_dotenv
from discord.ext import commands, tasks
from datetime import datetime, time, timedelta
# Get bot key from environment.
load_dotenv()
auth = os.getenv("DISCORD_KEY")
# Set Bot prefix
prefix = 'gov!'

# Set name for uncogged commands
help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)

# Set status for the bot, showing how to run the help command
activity = discord.Activity(name='Governance', type=discord.ActivityType.watching)

# Instantiate the bot
bot = commands.Bot(command_prefix=prefix, help_command=help_command, activity=activity)
WHEN = time(14, 5, 50)  # 00:00 UTC

# Status dictionary
status = {
    '00': 'Temp Check | 72h',
    '01': 'Temp Check | 48',
    '02': 'Temp Check | 24h',
    '03': 'Snapshot Vote | 96h',
    '04': 'Snapshot Vote | 72h',
    '05': 'Snapshot Vote | 48h',
    '06': 'Snapshot Vote | 24h',
    '07': 'Multisig Exec | 96h',
    '08': 'Multisig Exec | 72h',
    '09': 'Multisig Exec | 48',
    '10': 'Multisig Exec | 24h',
    '11': 'Delay Period | 72h',
    '12': 'Delay Period | 48h',
    '13': 'Delay Period | 24h',
}




async def gov_cycle():
    with open('data.json', 'r') as file:
        env = json.load(file)

        
    channel_id = env["CHANNEL_ID"]
    today = "%02d" % (env["CURRENT_DAY"],)
    daily_image = f"resources/day{today}/{today}.png"
    daily_thumb = f"resources/day{today}/thumbnail.png"

    if env["YESTERDAY_ID"] !=0:
        channel = bot.get_channel(channel_id)
        msg = await channel.fetch_message(str(env["YESTERDAY_ID"]))
        await msg.delete()       

 
    

    embed = Embed(
        title = 'Governance Update',
        description = f"**Hey Baker!**\n\nToday is day {env['CURRENT_DAY']+1} of our Governance Cycle."
        )

    image = discord.File(daily_image, filename="image.png")
    embed.set_image(url="attachment://image.png")

    thumb = discord.File(daily_thumb, filename="thumb.png")
    embed.set_thumbnail(url="attachment://thumb.png")
    
    files = [image, thumb]

    await bot.wait_until_ready() # This step is necessary to make sure the bot is ready to send
    channel = bot.get_channel(channel_id)
    msg = await channel.send(files=files, embed=embed)

    await bot.change_presence(activity= discord.Activity(type=discord.ActivityType.watching, name=f"{status[today]}"))
    env["CURRENT_DAY"] = (env["CURRENT_DAY"] + 1) % 14
    env["YESTERDAY_ID"] = msg.id

    with open('data.json', 'w') as file:
        json.dump(env, file)



async def background_task():
    now = datetime.utcnow()
    if now.time() > WHEN:  # Make sure loop doesn't start after {WHEN} as then it will send immediately the first time as negative seconds will make the sleep yield instantly
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
        seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
        print("waiting for " + str(seconds))
        await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start 
    while True:
        now = datetime.utcnow() # You can do now() or a specific timezone if that matters, but I'll leave it with utcnow
        target_time = datetime.combine(now.date(), WHEN)  # 22:00 PM today (In UTC)
        seconds_until_target = (target_time - now).total_seconds()
        await asyncio.sleep(seconds_until_target)  # Sleep until we hit the target time
        await gov_cycle()  # Call the helper function that sends the message
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
        seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
        await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start a new iteration



if __name__ == "__main__":
    bot.loop.create_task(background_task())
    bot.run(auth)
