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
WHEN = time(20, 00, 00)  # 20:00 UTC

# Status dictionary
status = {
    '00': 'Temp Check | 7d',
    '01': 'Temp Check | 6d',
    '02': 'Temp Check | 5d',
    '03': 'Temp Check | 96h',
    '04': 'Temp Check | 72h',
    '05': 'Contributor Vote | 96h',
    '06': 'Contributor Vote | 72h',
    '07': 'Contributor Vote | 48h',
    '08': 'Contributor Vote | 24h',
    '09': 'Multisig Exec | 72h',
    '10': 'Multisig Exec | 48h',
    '11': 'Multisig Exec | 24h',
    '12': 'Delay Period | 48h',
    '13': 'Delay Period | 24h',
}
# message dictionary
message = {
    '00': "Hey Canu Crew! Phase 1 (Temperature Check) has now begun. Any CanuDAO community member can submit their proposal drafts to <#897161655706861639> within the next 5 days. Everyone is encouraged to leave feedback and emoji-react!",

    '01': "Hey Canu Crew! Phase 2 (Contributor Voting) has now begun. All drafts from Phase 1 that received 5+ positive reactions have moved to #vote. Both <@&893255678800564236> and <@&893306804828790835> can vote on these proposals within the next 4 days!",

    '02': "Hey Canu Crew! Phase 3 (Multisig Execution) has now begun. <@&968975088953208902> contributors have 72 hours to queue and sign any reconfigurations in CanuDAO's multisig from Phase 2 proposals that scored a net positive of 5 votes.",

    '03': "Hey Canu Crew! Phase 4 (Delay Period) has now begun. Reconfigurations must be submitted at least 2 days before the start of the next funding cycle. During this period contributors have time to verify queued reconfigurations and proposals, and for CND holders to burn their tokens if desired."
}


async def gov_cycle():
    with open('data.json', 'r') as file:
        env = json.load(file)
    # 0, 5, 9, 12
    send = False
    channel_id = env["CHANNEL_ID"]
    today = "%02d" % (env["CURRENT_DAY"],)
    _today = int(today)

    if _today == 12:
        daily_image = f"resources/day03/03.png"
        msg = message['03']
        send = True
    elif _today == 9:
        daily_image = f"resources/day02/02.png"
        msg = message['02']
        send = True
    elif _today == 5:
        daily_image = f"resources/day01/01.png"
        msg = message['01']
        send = True
    elif _today == 0:
        daily_image = f"resources/day00/00.png"
        msg = message['00']
        send = True

    #if env["YESTERDAY_ID"] !=0:
    #    channel = bot.get_channel(channel_id)
    #    msg = await channel.fetch_message(str(env["YESTERDAY_ID"]))
    #    await msg.delete()       

 
    
    if send:
        embed = Embed(
            title = 'Governance Update',
            description = f"**Hey Canu Crew!!**\n\n{msg}"
            )

        image = discord.File(daily_image, filename="image.png")
        embed.set_image(url="attachment://image.png")
        
        files = [image]

        await bot.wait_until_ready() # This step is necessary to make sure the bot is ready to send
        channel = bot.get_channel(channel_id)
        msg = await channel.send(files=files, embed=embed)
        env["YESTERDAY_ID"] = msg.id

    await bot.change_presence(activity= discord.Activity(type=discord.ActivityType.watching, name=f"{status[today]}"))
    env["CURRENT_DAY"] = (env["CURRENT_DAY"] + 1) % 14
    

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
