import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from python_aternos import Client, ServerStartError

serverAddress = 'none'

#NOTE - Discord section
def runDiscordBot():

    load_dotenv()
    # TOKEN = os.getenv('DISCORD_TOKEN')

    # intents = discord.Intents.default()
    # intents.message_content = True

    # bot = commands.Bot(command_prefix= '/' , intents=intents)

    bot = discord.Bot()

    @bot.event
    async def on_ready():
        print(f"{bot.user} is ready and online!")

    @bot.command(description="Sends the bot's latency.")
    async def ping(ctx):
        title = 'Aternos Server Controller'
        descr = ('Pong! Latency is '+str(bot.latency))
        embed = createEmbed(title, descr)
        await ctx.respond(embed=embed)

    @bot.command(description='Sets the Aternos server address.')
    async def set(ctx, my_server_address):
        global serverAddress
        serverAddress = my_server_address
        title = 'Server address set correctly!'
        embed = createEmbed(title)
        await ctx.respond(embed=embed)

    @bot.command(description='Shows current Aternos server address.')
    async def view(ctx):
        title = 'The current server address is: '
        embed = createEmbed(title, serverAddress)
        await ctx.respond(embed=embed)

    @bot.command(description='Shows helpful commands list.')
    async def help(ctx):
        title = 'Commands list: '
        embed = createEmbed(title)
        await ctx.respond(embed=embed)

    @bot.command(description='Starts your Aternos server.')
    async def start(ctx):
        status = serverStatus()
        title = 'Server status: '
        starting = 'Server starting..'
        online = 'Server online'
        if status == 'offline':
            runServer()
            embed = createEmbed(title, starting)
            await ctx.respond(embed=embed)
        elif status == 'loading' or status == 'preparing':
            embed = createEmbed(title, starting)
            await ctx.respond(embed=embed)
        elif status == 'online':
            embed = createEmbed(title, online)
            await ctx.respond(embed=embed)

    @bot.command(description='Shows current Aternos server status.')
    async def status(ctx):
        status = serverStatus()
        title = 'The server is:'
        embed = createEmbed(title, status)
        await ctx.respond(embed=embed)

    @bot.command(description='Stops your Aternos server.')
    async def stop(ctx):
        status = serverStatus()
        title = 'Server status: '+status
        online = 'Server shutting down..'
        loading = 'Server starting, you can\'t stop it now.\nTry when the server is online!'
        offline = 'Server offline'
        if status == 'online':
            stopServer()
            embed = createEmbed(title, online)
            await ctx.respond(embed=embed)
        elif status == 'loading' or status == 'preparing':
            embed = createEmbed(title, loading)
            await ctx.respond(embed=embed)
        elif status == 'offline':
            embed = createEmbed(title, offline)
            await ctx.respond(embed=embed)

    @bot.command(description='Shows number of current online players.')
    async def onlineplayers(ctx):
        status = serverStatus()
        titleOnline = 'Current number of players'
        titleOffline = 'The server is offline!'
        if status == 'online':
            rs = getOnlinePlayers()
            embed = createEmbed(titleOnline, str(rs))
            await ctx.respond(embed=embed)
        else:
            embed = createEmbed(titleOffline)
            await ctx.respond(embed=embed)
    
    @bot.command(description='Shows a list of current online players.')
    async def playerlist(ctx):
        rs = getPlayerList()
        title = 'Player list'
        descr = '\n'.join(rs)
        embed = createEmbed(title, descr)
        await ctx.respond(embed=embed)

    @bot.command(description='Provides general info of your Aternos server.')
    async def info(ctx):
        statusTitle = 'Server status'
        status = serverStatus()
        title = 'General info'
        onlinePlayersTitle = 'Online Players'
        onlineP = getOnlinePlayers()
        playerListTitle = 'Player List'
        playerList = getPlayerList()
        playerListProcessed = '\n'.join(playerList)
        embed = createEmbed(title, '', statusTitle, status, onlinePlayersTitle, onlineP, playerListTitle, playerListProcessed)
        await ctx.respond(embed=embed)

    bot.run(os.getenv('DISCORD_TOKEN'))

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

def getOnlinePlayers():
    aternos = Client.from_hashed('Ho3pLi', '2f37ce8d68dea0676ba16ea100ba87e2')

    servers = aternos.list_servers()

    myServer = None

    for server in servers:
        if server.address == serverAddress:
            myServer = server
        
    return ('Online: '+str(myServer.players_count)+' of '+str(myServer.slots))

def getPlayerList():
    aternos = Client.from_hashed('Ho3pLi', '2f37ce8d68dea0676ba16ea100ba87e2')

    servers = aternos.list_servers()

    myServer = None

    for server in servers:
        if server.address == serverAddress:
            myServer = server
        
    return myServer.players_list

#NOTE - other suff

def createEmbed(title, description='', param1_name='', param1_value='', param2_name='', param2_value='', param3_name='', param3_value=''):
    embed = discord.Embed(
        title=title,
        description=description,
        type='rich'
    )

    if param1_name != '' and param1_value != '':
        embed.add_field(name=param1_name, value=param1_value)
        if param2_name != '' and param2_value != '':
            embed.add_field(name=param2_name, value=param2_value)
            if param3_name != '' and param3_value != '':
                embed.add_field(name=param3_name, value=param3_value)

    return embed
