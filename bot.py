import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from python_aternos import Client, ServerStartError

serverAddress = 'none'

#NOTE - Discord section
def runDiscordBot():

    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix= '/' , intents=intents)

    @bot.command()
    async def setSA(ctx, myServerAddress):
        global serverAddress
        serverAddress = myServerAddress
        await ctx.channel.send('Server address set correctly!')

    @bot.command()
    async def viewSA(ctx):
        await ctx.channel.send('The current server address is: `'+serverAddress+'`')

    @bot.command()
    async def helpASC(ctx):
        await ctx.channel.send('List of helpful commands :)\n\n```/viewSA: check current Server Address\n\n/setSA: set your Server Address\n\n/statusASC: check your server current status\n\n/startASC: start your server\n\n/stopASC: shut down your server```')

    @bot.command()
    async def startASC(ctx):
        status = serverStatus()
        print(status)
        if status == 'offline':
            runServer()
            await ctx.channel.send('Server status: '+status+'\n\nServer starting..')
        elif status == 'loading' or status == 'preparing':
            await ctx.channel.send('Server status: '+status+'\n\nServer starting..')
        elif status == 'online':
            await ctx.channel.send('Server status: '+status+'\n\nServer online')

    @bot.command()
    async def statusASC(ctx):
        status = serverStatus()
        await ctx.channel.send('The server is: '+status)

    @bot.command()
    async def stopASC(ctx):
        status = serverStatus()
        if status == 'online':
            stopServer()
            await ctx.channel.send('Server status: '+status+'\n\nServer shutting down..')
        elif status == 'loading' or status == 'preparing':
            await ctx.channel.send('Server status: '+status+'\n\nServer starting, you can\'t stop it now.\nTry when the server is online!')
        elif status == 'offline':
            await ctx.channel.send('Server status: '+status+'\n\nServer offline')

    bot.run(TOKEN)

#NOTE - Aternos section

def serverStatus() -> str:
    aternos = Client.from_hashed('Ho3pLi', '2f37ce8d68dea0676ba16ea100ba87e2')

    servers = aternos.list_servers()

    myServer = None

    for server in servers:
        if server.address == serverAddress:
            myServer = server
    
    return myServer.status

def runServer():
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

def stopServer():
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