from os import walk
from pathlib import Path

import discord
from discord import option
from bot import bot

global play_sound
global options


async def init(play_function):
    global play_sound
    global options

    options = []

    play_sound = play_function

    # Get the file names within the pay_to_play folder
    filenames = next(walk("../downloads/pay_to_play"), (None, None, []))[2]

    for i in range(len(filenames)):
        filenames[i] = Path(filenames[i]).stem

        options.append(discord.SelectOption(
                label=filenames[i],
                value=filenames[i]
            )
        )
