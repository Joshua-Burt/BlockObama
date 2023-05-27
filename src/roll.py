import random
import re
import discord
from discord import option

from bot import bot


class Roll:
    def __init__(self, num_of_rolls, operation, modifier, max_num):
        self.num_of_rolls = num_of_rolls
        self.operation = operation
        self.modifier = modifier
        self.max_num = max_num


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

    await roll_using_notation(ctx, roll_str)


async def roll_using_notation(ctx, raw_roll):
    roll_obj = prepare_roll(raw_roll.replace(" ", ""))
    random_num = 0
    modified_num = 0
    num = 0

    # Generate a random number using the max roll as many times as there are rolls. Add each roll together.
    if not roll_obj:
        await ctx.respond("Invalid input")
        return False
    else:
        for i in range(0, roll_obj.num_of_rolls):
            random_num = random.randint(1, roll_obj.max_num)
            num += random_num

    # Add or subtract the modifier value from the random number, and set it to a new variable.
    if roll_obj.operation == '+':
        modified_num = num + roll_obj.modifier
    elif roll_obj.operation == '-':
        modified_num = num - roll_obj.modifier

    if roll_obj.max_num == 2 and 1 <= modified_num <= 2:
        await ctx.respond(file=discord.File('img\\dice\\d2\\d2-' + str(modified_num) + '.jpg'))
        if random_num == '1':
            await ctx.send('It\'s heads!')
        else:
            await ctx.send('It\'s tails!')
        return

    # Identifies the maximum roll, and if the total roll is <= to it, returns an image of that die and number
    elif roll_obj.max_num == 4 and 1 <= modified_num <= 4:
        await ctx.respond(file=discord.File('img\\dice\\d4\\d4-' + str(modified_num) + '.png'))
    elif roll_obj.max_num == 6 and 1 <= modified_num <= 6:
        await ctx.respond(file=discord.File('img\\dice\\d6\\d6-' + str(modified_num) + '.png'))
    elif roll_obj.max_num == 8 and 1 <= modified_num <= 8:
        await ctx.respond(file=discord.File('img\\dice\\d8\\d8-' + str(modified_num) + '.png'))
    elif roll_obj.max_num == 10 and 1 <= modified_num <= 10:
        await ctx.respond(file=discord.File('img\\dice\\d10\\d10-' + str(modified_num) + '.png'))
    elif roll_obj.max_num == 12 and 1 <= modified_num <= 12:
        await ctx.respond(file=discord.File('img\\dice\\d12\\d12-' + str(modified_num) + '.png'))
    elif roll_obj.max_num == 20 and 1 <= modified_num <= 20:
        await ctx.respond(file=discord.File('img\\dice\\d20\\d20-' + str(modified_num) + '.png'))

    # send the message containing the roll info if there was a specified modifier. Otherwise, just respond the result.
    if roll_obj.modifier != 0:
        await ctx.respond("> " + str(num) + " " + roll_obj.operation + " "
                          + str(roll_obj.modifier) + " = " + str(modified_num))
    else:
        await ctx.respond("> " + str(num))


# Inputs a string in the format of a D&D roll (e.g. 2d20 + 2) and extracts the information and finally returns an object
# of type Roll that contains all the important information. In the case of invalid input, returns false.
def prepare_roll(raw_roll):
    # Find where the 'd' in the message is to use as an anchor
    d_pos = raw_roll.find('d')

    # If the 'd' exists, and it's not the last character of the message
    if d_pos != -1 and len(raw_roll) > d_pos + 1:
        # Checking if there are multiple rolls by seeing if the first character is a digit or not
        if raw_roll[0].isdigit():
            num_of_rolls = int(re.match('\d+(?=d)', raw_roll)[0])
        elif raw_roll[0] == "d":
            num_of_rolls = 1
        else:
            return False
    else:
        return False

    # Finds the maximum number that comes before + or -
    max_num = int(re.findall('(?<=d)\d+(?=$|\D)', raw_roll)[0])

    matches = ['+', '-']

    if any(x in raw_roll for x in matches):
        # Finds the operation, either + or -
        operation = re.findall('\W', raw_roll)[0]
        # Finds the modifier that comes after + or -
        modifier = int(re.findall('(?<=\W)\d+', raw_roll)[0])
    else:
        # Sets the operator and modifier to +0, as there was no specified modifier
        operation = "+"
        modifier = 0

    roll_obj = Roll(num_of_rolls, operation, modifier, max_num)

    return roll_obj
