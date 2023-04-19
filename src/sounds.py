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


@bot.slash_command(name="roll", description="Roll a number of various sided dice")
@option(
    "modifier",
    description="How much to add/subtract from the total roll",
    required=False,
    default=0
)
async def roll(ctx, number_of_dice, number_of_faces, modifier):
    if int(modifier) >= 0:
        roll_str = f"{number_of_dice}d{number_of_faces} + {modifier}"
    else:
        roll_str = f"{number_of_dice}d{number_of_faces} - {abs(int(modifier))}"

    await rl.roll(ctx, roll_str)