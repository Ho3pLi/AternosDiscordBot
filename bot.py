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
        title = 'Server address set correctly!'
        embed = createEmbed(title)
        await ctx.channel.send(embed=embed)

    @bot.command()
    async def viewSA(ctx):
        title = 'The current server address is: '
        embed = createEmbed(title, serverAddress)
        await ctx.channel.send(embed=embed)

    @bot.command()
    async def helpASC(ctx):
        await ctx.channel.send('List of helpful commands :)\n\n```/viewSA: check current Server Address\n\n/setSA: set your Server Address\n\n/statusASC: check your server current status\n\n/startASC: start your server\n\n/stopASC: shut down your server```')

    @bot.command()
    async def startASC(ctx):
        status = serverStatus()
        title = 'Server status: '
        starting = 'Server starting..'
        online = 'Server online'
        if status == 'offline':
            runServer()
            embed = createEmbed(title, starting)
            await ctx.channel.send(embed=embed)
        elif status == 'loading' or status == 'preparing':
            embed = createEmbed(title, starting)
            await ctx.channel.send(embed=embed)
        elif status == 'online':
            embed = createEmbed(title, online)
            await ctx.channel.send(embed=embed)

    @bot.command()
    async def statusASC(ctx):
        status = serverStatus()
        title = 'The server is:'
        embed = createEmbed(title, status)
        await ctx.channel.send(embed=embed)

    @bot.command()
    async def stopASC(ctx):
        status = serverStatus()
        title = 'Server status: '+status
        online = 'Server shutting down..'
        loading = 'Server starting, you can\'t stop it now.\nTry when the server is online!'
        offline = 'Server offline'
        if status == 'online':
            stopServer()
            embed = createEmbed(title, online)
            await ctx.channel.send(embed=embed)
        elif status == 'loading' or status == 'preparing':
            embed = createEmbed(title, loading)
            await ctx.channel.send(embed=embed)
        elif status == 'offline':
            embed = createEmbed(title, offline)
            await ctx.channel.send(embed=embed)

    @bot.command()
    async def onlinePlayers(ctx):
        status = serverStatus()
        titleOnline = 'Current number of players'
        titleOffline = 'The server is offline!'
        if status == 'online':
            rs = getOnlinePlayers()
            embed = createEmbed(titleOnline, str(rs))
            await ctx.channel.send(embed=embed)
        else:
            embed = createEmbed(titleOffline)
            await ctx.channel.send(embed=embed)
    
    @bot.command()
    async def playerList(ctx):
        rs = getPlayerList()
        title = 'Player list'
        descr = '\n'.join(rs)
        embed = createEmbed(title, descr)
        await ctx.channel.send(embed=embed)

    @bot.command()
    async def infoASC(ctx):
        statusTitle = 'Server status'
        status = serverStatus()
        title = 'General info'
        onlinePlayersTitle = 'Online Players'
        onlineP = getOnlinePlayers()
        playerListTitle = 'Player List'
        playerList = getPlayerList()
        playerListProcessed = '\n'.join(playerList)
        embed = createEmbed(title, '', statusTitle, status, onlinePlayersTitle, onlineP, playerListTitle, playerListProcessed)
        await ctx.channel.send(embed=embed)

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
