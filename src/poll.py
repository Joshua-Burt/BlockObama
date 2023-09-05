import discord
from discord import option

from bot import bot


class TwoOption(discord.ui.View):
    @discord.ui.button(label="Option 1", row=0, style=discord.ButtonStyle.primary)
    async def first_button_callback(self, button, interaction):
        await edit_message(interaction, 1)

    @discord.ui.button(label="Option 2", row=0, style=discord.ButtonStyle.primary)
    async def second_button_callback(self, button, interaction):
        await edit_message(interaction, 2)


class ThreeOption(discord.ui.View):
    @discord.ui.button(label="Option 1", row=0, style=discord.ButtonStyle.primary)
    async def first_button_callback(self, button, interaction):
        await edit_message(interaction, 1)

    @discord.ui.button(label="Option 2", row=0, style=discord.ButtonStyle.primary)
    async def second_button_callback(self, button, interaction):
        await edit_message(interaction, 2)

    @discord.ui.button(label="Option 3", row=0, style=discord.ButtonStyle.primary)
    async def third_button_callback(self, button, interaction):
        await edit_message(interaction, 3)


class FourOption(discord.ui.View):
    @discord.ui.button(label="Option 1", row=0, style=discord.ButtonStyle.primary)
    async def first_button_callback(self, button, interaction):
        await edit_message(interaction, 1)

    @discord.ui.button(label="Option 2", row=0, style=discord.ButtonStyle.primary)
    async def second_button_callback(self, button, interaction):
        await edit_message(interaction, 2)

    @discord.ui.button(label="Option 3", row=1, style=discord.ButtonStyle.primary)
    async def third_button_callback(self, button, interaction):
        await edit_message(interaction, 3)

    @discord.ui.button(label="Option 4", row=1, style=discord.ButtonStyle.primary)
    async def fourth_button_callback(self, button, interaction):
        await edit_message(interaction, 4)


@option("option3", description="Third poll option", required=False, default="")
@option("option4", description="Fourth poll option", required=False, default="")
@bot.slash_command(name="poll", description="Create a poll")
async def button(ctx, title, option1, option2,
                 option3: discord.Option(str) = "",
                 option4: discord.Option(str) = ""):
    options_string = await choices_to_string(option1, option2, option3, option4)
    header_message = "**Poll for: \"" + title + "\"**\n" + options_string

    # No options given
    if option1 == "" or option2 == "":
        await ctx.respond("You must provide at least two options")
        return

    # 4 options given
    if option3 != "" and option4 != "":
        await ctx.respond(header_message, view=FourOption(timeout=None))
        return

    # 3 options given
    if option3 != "":
        await ctx.respond(header_message, view=ThreeOption(timeout=None))
        return

    # 2 options given
    await ctx.respond(header_message, view=TwoOption(timeout=None))


async def edit_message(interaction, row):
    new_message_content = await add_vote(interaction.message.content, row)
    await interaction.message.edit(new_message_content)
    await interaction.response.defer()


async def add_vote(original_message, option_number):
    lines = original_message.splitlines()
    lines[option_number] += "x"
    return "\n".join(lines)


async def choices_to_string(option1, option2, option3, option4):
    output_string = "Option 1: *" + option1 + "* - \nOption 2: *" + option2 + "* - "
    if option3 != "":
        output_string += "\nOption 3: *" + option3 + "* - "

    if option4 != "":
        output_string += "\nOption 4: *" + option4 + "* - "

    return output_string
