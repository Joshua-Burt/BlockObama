import os
import subprocess
import time
import discord
import socket

global process
process = None


async def start(ctx, bot):
    global process

    if process:
        await ctx.send("The server is already running")
        print("Server is already running")
    else:
        os.chdir("C:\\Users\\Turtl\\Desktop\\ModdedServer")

        process = subprocess.Popen(['start.bat'], stdin=subprocess.PIPE, encoding='utf8')

        time.sleep(50)

        os.chdir("C:\\Users\\Turtl\\PycharmProjects\\BlockObama 2.0")

        # TODO: Check for server being online
        # loop_count = 0
        # while not await check_server_status():
        #     print("Checking server status...")
        #     time.sleep(2)
        #     loop_count += 2
        #
        #     if loop_count == 30:
        #         ctx.send("I can't tell if the server is running or not, but it's been long enough that it probably is")
        #         break

        game = discord.Game("Minecraft")
        await bot.change_presence(status=discord.Status.online, activity=game)

        await ctx.send("Server started, probably")


async def stop(ctx):
    global process
    if process:
        await server_command("stop")
        await ctx.send("Stopped the server")
        process = None
        os.chdir("C:\\Users\\Turtl\\PycharmProjects\\BlockObama 2.0")
    else:
        await ctx.send("The server isn't running")


async def ping_ip(ip, port):
    a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    location = (ip, port)
    result_of_check = a_socket.connect_ex(location)

    a_socket.close()

    if result_of_check == 0:
        print("{}:{} is open".format(ip, port))
        return True
    else:
        print("{}:{} is not open".format(ip, port))
        return False


async def server_command(command):
    global process
    output = process.communicate(command, timeout=10)[0]


async def check_server_status():
    status = await ping_ip("198.90.95.248", 25565)

    return status
