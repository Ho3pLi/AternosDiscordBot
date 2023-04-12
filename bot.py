import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from python_aternos import Client, ServerStartError

#NOTE - Discord section
def runDiscordBot():

    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix= '/' , intents=intents)

    @bot.command()
    async def helpASC(ctx):
        await ctx.channel.send('`List of helpful commands coming soon :)`')

    @bot.command()
    async def startASC(ctx, serverAddress):
        status = serverStatus(serverAddress)
        print(status)
        if status == 'offline':
            runServer(serverAddress)
            await ctx.channel.send('Server status: '+status+'\n\nServer starting..')
        elif status == 'loading' or status == 'preparing':
            await ctx.channel.send('Server status: '+status+'\n\nServer starting..')
        elif status == 'online':
            await ctx.channel.send('Server status: '+status+'\n\nServer online')

    @bot.command()
    async def statusASC(ctx, serverAddress):
        status = serverStatus(serverAddress)
        await ctx.channel.send('The server is: '+status)

    @bot.command()
    async def stopASC(ctx, serverAddress):
        status = serverStatus(serverAddress)
        if status == 'online':
            stopServer(serverAddress)
            await ctx.channel.send('Server status: '+status+'\n\nServer shutting down..')
        elif status == 'loading' or status == 'preparing':
            await ctx.channel.send('Server status: '+status+'\n\nServer starting, you can\'t stop it now.\nTry when the server is online!')
        elif status == 'offline':
            await ctx.channel.send('Server status: '+status+'\n\nServer offline')

    bot.run(TOKEN)

#NOTE - Aternos section

def serverStatus(serverAddress: str) -> str:
    aternos = Client.from_hashed('Ho3pLi', '2f37ce8d68dea0676ba16ea100ba87e2')

    servers = aternos.list_servers()

    myServer = None

    for server in servers:
        if server.address == serverAddress:
            myServer = server
    
    return myServer.status

def runServer(serverAddress: str):
    aternos = Client.from_hashed('Ho3pLi', '2f37ce8d68dea0676ba16ea100ba87e2')

    servers = aternos.list_servers()

    myServer = None

    for server in servers:
        if server.address == serverAddress:
            myServer = server
    
    try:
        myServer.start()
    except ServerStartError as err:
        print(err.code)
        print(err.message)

def stopServer(serverAddress: str):
    aternos = Client.from_hashed('Ho3pLi', '2f37ce8d68dea0676ba16ea100ba87e2')

    servers = aternos.list_servers()

    myServer = None

    for server in servers:
        if server.address == serverAddress:
            myServer = server
    
    try:
        myServer.stop()
    except ServerStartError as err:
        print(err.code)
        print(err.message)