import time

import discord
from discord import option

from bot import bot

active_polls = []


class TwoOption(discord.ui.View):
    @discord.ui.button(label="Option 1", row=0, style=discord.ButtonStyle.primary)
    async def first_button_callback(self, button, interaction: discord.Interaction):
        await add_vote(interaction, 1)

    @discord.ui.button(label="Option 2", row=0, style=discord.ButtonStyle.primary)
    async def second_button_callback(self, button, interaction):
        await add_vote(interaction, 2)


class ThreeOption(discord.ui.View):
    @discord.ui.button(label="Option 1", row=0, style=discord.ButtonStyle.primary)
    async def first_button_callback(self, button, interaction):
        await add_vote(interaction, 1)

    @discord.ui.button(label="Option 2", row=0, style=discord.ButtonStyle.primary)
    async def second_button_callback(self, button, interaction):
        await add_vote(interaction, 2)

    @discord.ui.button(label="Option 3", row=0, style=discord.ButtonStyle.primary)
    async def third_button_callback(self, button, interaction):
        await add_vote(interaction, 3)


class FourOption(discord.ui.View):
    async def on_timeout(self):
        self.disable_all_items()

    @discord.ui.button(label="Option 1", row=0, style=discord.ButtonStyle.primary)
    async def first_button_callback(self, button, interaction):
        await add_vote(interaction, 1)

    @discord.ui.button(label="Option 2", row=0, style=discord.ButtonStyle.primary)
    async def second_button_callback(self, button, interaction):
        await add_vote(interaction, 2)

    @discord.ui.button(label="Option 3", row=1, style=discord.ButtonStyle.primary)
    async def third_button_callback(self, button, interaction):
        await add_vote(interaction, 3)

    @discord.ui.button(label="Option 4", row=1, style=discord.ButtonStyle.primary)
    async def fourth_button_callback(self, button, interaction):
        await add_vote(interaction, 4)


@option("timeout", description="Number of hours before poll expires")
@bot.slash_command(name="poll", description="Create a poll")
async def button(ctx, title, option1, option2,
                 option3: discord.Option(str) = "",
                 option4: discord.Option(str) = "",
                 timeout: float = 1):

    # Convert given number from hours into seconds
    timeout *= 3600

    expiry_time = round(time.time() + timeout)
    timestamp_string = f"Expires <t:{expiry_time}:R>"

    options_string = await choices_to_string(option1, option2, option3, option4)
    header_message = "**Poll for: \"" + title + "\"** - " + timestamp_string + "\n" + options_string

    # No options given
    if option1 == "" or option2 == "":
        await ctx.respond("You must provide at least two options")
        return

    # 4 options given
    if option3 != "" and option4 != "":
        await ctx.respond(header_message, view=FourOption(timeout=timeout))
        return

    # 3 options given, option3 is empty but option4 is filled. option4 is now option 3
    if option3 == "" and option4 != "":
        await ctx.respond(header_message, view=ThreeOption(timeout=timeout))
        return

    # 3 options given
    if option3 != "":
        await ctx.respond(header_message, view=ThreeOption(timeout=timeout))
        return

    # 2 options given
    await ctx.respond(header_message, view=TwoOption(timeout=timeout))


async def add_vote(interaction: discord.Interaction, option_choice):
    if await has_user_voted(interaction):
        await interaction.response.defer()
        return

    # Adds a vote to active poll
    # If the poll doesn't exist in the array, it adds one
    await add_vote_to_poll(interaction)

    await edit_message(interaction, option_choice)
    await interaction.response.defer()


async def has_user_voted(interaction: discord.Interaction):
    poll = await get_from_active_polls(interaction)

    if poll is None:
        return False
    else:
        return interaction.user.id in poll["users"]


async def add_vote_to_poll(interaction: discord.Interaction):
    # User has voted, don't add to poll and return
    if await has_user_voted(interaction):
        return

    poll = await get_from_active_polls(interaction)

    # Add the user if the poll exists, otherwise add a new poll and add the user
    if poll is not None:
        poll["users"].append(interaction.user.id)
    else:
        dictionary = {
            "message": interaction.message,
            "users": [interaction.user.id]
        }
        active_polls.append(dictionary)


async def get_from_active_polls(interaction: discord.Interaction):
    for i in range(len(active_polls)):
        if active_polls[i]["message"] == interaction.message:
            return active_polls[i]
    return None


async def edit_message(interaction, row):
    new_message_content = await append_vote_to_line(interaction.message.content, row)
    await interaction.message.edit(new_message_content)


# String manipulation functions

async def append_vote_to_line(original_message, line_number):
    lines = original_message.splitlines()
    lines[line_number] += "x"
    return "\n".join(lines)


async def choices_to_string(option1, option2, option3, option4):
    output_string = "Option 1: *" + option1 + "* - \nOption 2: *" + option2 + "* - "

    # Special case: If option 3 is empty, but option 4 is given, option 4 is displayed as option 3 in the message
    if option3 == "" and option4 != "":
        output_string += "\nOption 3: *" + option4 + "* - "
        return output_string

    if option3 != "":
        output_string += "\nOption 3: *" + option3 + "* - "

    if option4 != "":
        output_string += "\nOption 4: *" + option4 + "* - "

    return output_string
