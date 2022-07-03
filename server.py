import os
import socket
import subprocess
import time
import discord


async def start(ctx, bot):
    status = await check_server_status()

    if status:
        await ctx.send("The server is already running")
        print("Server is already running")
    else:
        os.chdir("C:\\Users\\Turtl\\Desktop\\Minecraft Forge Server")

        process = subprocess.Popen(['run.bat'], stdin=subprocess.PIPE)

        time.sleep(5)

        while not await check_server_status():
            print("Checking server status...")
            time.sleep(2)

        game = discord.Game("Minecraft")
        await bot.change_presence(status=discord.Status.online, activity=game)

        await ctx.send("Server started, probably")


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


async def check_server_status():
    status = await ping_ip("198.90.95.248", 25565)

    return status
