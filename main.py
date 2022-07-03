from time import sleep
from discord.ext import commands

import discord
import roll as rl
import server as mcserver
import json

DISCORD_TOKEN = 'Nzk3NjUxNTc0OTQ3MTg0NzEw.X_pk6w.uO-sRng69YLuWrIBDEr9KHNLDfY'

DAVID_ID = 41641570832351234
MORGAN_ID = 429659989750317076
QUINN_ID = 325111288764170240
JACOB_ID = 416415943896596493

global json_file

bot = commands.Bot(command_prefix="!ob ")


@bot.event
async def on_ready():
    # Startup printing, username, etc.
    print('Powered on [o.o]\n'
          'Logged in as {0.user}'.format(bot))
    print("-----------------------------")

    game = discord.Game("not Minecraft")
    await bot.change_presence(status=discord.Status.online, activity=game)

    with open('settings.json', 'r') as f:
        data = json.load(f)

    global json_file
    json_file = data


@bot.command(pass_context=True)
async def say(ctx, message):
    await ctx.message.delete()
    await ctx.send(message)


@bot.command()
async def mock(ctx):
    logs = await ctx.channel.history(limit=2).flatten()

    if logs[1].author == bot.user:
        await ctx.send('no')
    else:
        in_str = logs[1].content
        await ctx.send(await mockify(in_str))


@bot.command()
async def roll(ctx, input_string):
    await rl.roll(ctx, input_string)


@bot.command()
async def start(ctx):
    await ctx.send("Starting server...")
    await mcserver.start(ctx, bot)


# Take the last message sent and repeats it with alternating capitals
# e.g. "Spongebob" -> "SpOnGeBoB"
async def mockify(in_str):
    new_string = ""
    temp = True  # true = uppercase, false = lowercase

    for i in in_str:
        if temp:
            new_string += i.upper()
        else:
            new_string += i.lower()
        if i != ' ':
            temp = not temp
    return new_string


@bot.command(aliases=['intro'])
async def toggle_play_on_enter(ctx):
    if "file_name" not in json_file[str(ctx.message.author.id)]:
        ctx.send("You don't have an intro at the moment")
        return

    json_file[str(ctx.message.author.id)]["play_on_enter"] = not json_file[str(ctx.message.author.id)]["play_on_enter"]

    with open('settings.json', 'w') as f:
        json.dump(json_file, f)

    await ctx.send(("Your intro is now ON" if json_file[str(ctx.message.author.id)]["play_on_enter"] else "Your intro is now OFF"))


async def play_sound(member, source):
    print(f'{member} has joined the vc')

    singing_channel = member.voice.channel
    await singing_channel.connect()

    bot.voice_clients[0].play(discord.FFmpegPCMAudio(executable="ffmpeg/bin/ffmpeg.exe", source=source))

    sleep(4)

    await bot.voice_clients[0].disconnect()


@bot.event
async def on_voice_state_update(member, before, after):
    if not before.channel and after.channel:

        if member.id == DAVID_ID and json_file[str(DAVID_ID)]["play_on_enter"]:
            await play_sound(member, "downloads/david_intro.mp3")
        elif member.id == MORGAN_ID and json_file[str(MORGAN_ID)]["play_on_enter"]:
            await play_sound(member, "downloads/morgan_intro.mp3")
        elif member.id == QUINN_ID and json_file[str(QUINN_ID)]["play_on_enter"]:
            await play_sound(member, "downloads/quinn_intro.mp3")
        elif member.id == JACOB_ID and json_file[str(JACOB_ID)]["play_on_enter"]:
            await play_sound(member, "downloads/jacob_intro.mp3")

bot.run(DISCORD_TOKEN)
