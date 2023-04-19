from pathlib import Path

import discord
from colorama import Fore
from discord import option
from mutagen.mp3 import MP3

from bot import bot
import json_utils
import sounds
from log import log

max_length = 0


async def init(max_intro_length):
    global max_length
    max_length = max_intro_length


@bot.slash_command(name="intro", description="Toggle your intro when joining a voice call")
async def intro(ctx):
    new_play_on_enter = not json_utils.get_user_field(ctx.author.id, "play_on_enter")
    json_utils.update_user(ctx.author.id, "play_on_enter", new_play_on_enter)

    await ctx.respond("Your intro is now " + ("ON" if new_play_on_enter else "OFF"), ephemeral=True)


@bot.slash_command(name="upload", description="Upload an .mp3 file to change your intro", )
@option(
    "attachment",
    discord.Attachment,
    description=f"An .mp3 file to be used as your intro. Max {str(max_length)} seconds.",
    required=True,
)
async def upload_intro(ctx: discord.ApplicationContext, attachment: discord.Attachment):
    if attachment.content_type == "audio/mpeg":
        file = await attachment.to_file()

        # Verify the length is less than the max
        if MP3(file.fp).info.length > max_length:
            await ctx.respond(f"Intros must be less than {str(max_length)}")
            return

        # Apply the new file
        file_name = json_utils.get_user_field(ctx.author.id, "file_name")

        await attachment.save(Path(str(Path.cwd()) + f"/../sounds/intros/{str(file_name)}"))

        await ctx.respond("Your intro has been changed")
        await log(f"Changed {Fore.YELLOW + str(ctx.author) + Fore.RESET}'s intro")
    else:
        await ctx.respond("Please upload an .mp3 file")


@bot.event
async def on_voice_state_update(member, before, after):
    if not before.channel and after.channel and not member.bot:
        if json_utils.get_user_field(member.id, "play_on_enter") is None:
            return

        await log("Playing {}\'s{} intro in {}".format(Fore.YELLOW + member.name, Fore.WHITE,
                                                       Fore.YELLOW + after.channel.name + Fore.RESET))
        await sounds.play_sound(member, "../sounds/intros/{}".format(json_utils.get_user_field(member.id, "file_name")))