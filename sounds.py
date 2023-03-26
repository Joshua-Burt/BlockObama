from os import walk
from pathlib import Path

import discord
from discord.ui import Item

global play_sound
global options


async def init(play_function):
    global play_sound
    global options
    options = []

    play_sound = play_function
    filenames = next(walk("downloads/pay_to_play"), (None, None, []))[2]
    for i in range(len(filenames)):
        filenames[i] = Path(filenames[i]).stem

        options.append(discord.SelectOption(
                label=filenames[i],
                value=filenames[i]
            )
        )

    # For sound selection
    # n = 25
    #
    # # using list comprehension
    # options = [options[i * n:(i + 1) * n] for i in range((len(options) + n - 1) // n)]


# async def create_select(ctx):
#     for i in range(len(options)):
#         SoundSelect()
#         await ctx.respond("Blah", view=thing, ephemeral=True)


class SoundSelect(discord.ui.View):
    choice = None

    def __new__(cls, *items: Item, choices):
        cls.choice = choices

    @discord.ui.select(  # the decorator that lets you specify the properties of the select menu
        placeholder="Choose a Sound!",  # the placeholder text that will be displayed if nothing is selected
        min_values=1,  # the minimum number of values that must be selected by the users
        max_values=1,  # the maximum number of values that can be selected by the users
        options=choice
    )
    async def select_callback(self, select, interaction: discord.Interaction):
        member = await interaction.guild.fetch_member(interaction.user.id)
        await interaction.response.send_message(f"Playing {select.values[0]}.mp3")
        await play_sound(member, "downloads/pay_to_play/" + select.values[0] + ".mp3")
