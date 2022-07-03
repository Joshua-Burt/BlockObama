from time import sleep

import discord
from discord.ext import commands
import roll as rl
import server as mcserver

DISCORD_TOKEN = 'Nzk3NjUxNTc0OTQ3MTg0NzEw.X_pk6w.uO-sRng69YLuWrIBDEr9KHNLDfY'

bot = commands.Bot(command_prefix="!ob ")


@bot.event
async def on_ready():
    # Startup printing, username, etc.
    print('Powered on [o.o]\n'
          'Logged in as {0.user}'.format(bot))
    print("-----------------------------")

    game = discord.Game("not Minecraft")
    await bot.change_presence(status=discord.Status.online, activity=game)


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

        if member.id == 41641570832351234:
            await play_sound(member, "downloads/filet.mp3")
        elif member.id == 429659989750317076:
            await play_sound(member, "downloads/morgan_intro.mp3")


bot.run(DISCORD_TOKEN)
