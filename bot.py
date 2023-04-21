import os
from dotenv import load_dotenv
import discord
from discord.utils import find
from python_aternos import Client, ServerStartError
import aiosqlite, asyncio

#NOTE - Discord section
def runDiscordBot():

    load_dotenv()
    # TOKEN = os.getenv('DISCORD_TOKEN')

    # intents = discord.Intents.default()
    # intents.message_content = True

    # bot = commands.Bot(command_prefix= '/' , intents=intents)

    bot = discord.Bot()

    #NOTE - DB section start
    async def dbSetup():
        bot.db = await aiosqlite.connect('storage.db')
        await bot.db.execute(
            '''
                CREATE TABLE IF NOT EXISTS "ServersAddresses" (
                "id" INTEGER NOT NULL,
                "discordServerId" TEXT NOT NULL UNIQUE,
                "aternosServerAddress" TEXT,
                PRIMARY KEY("id" AUTOINCREMENT)
                );
            '''
        )
        await bot.db.commit()
        await bot.db.close()

    async def drop(table):
        bot.db = await aiosqlite.connect('storage.db')
        await bot.db.execute(f'DROP TABLE "{table}"')
        await bot.db.commit()
        await bot.db.close()

    async def select(column, table, where=''):
        bot.db = await aiosqlite.connect('storage.db')
        rs = []
        if where=='':
            async with bot.db.execute(f"SELECT {column} FROM {table}") as cursor:
                async for row in cursor:
                    print(row)
                    rs.append(row)
        else:
            async with bot.db.execute(f"SELECT {column} FROM {table} WHERE {where}") as cursor:
                async for row in cursor:
                    rs.append(row)
                    rs = str(rs[0])[1:-2]
        await bot.db.close()
        return rs

    async def delete(table, where):
        bot.db = await aiosqlite.connect('storage.db')
        await bot.db.execute(f'DELETE FROM {table} WHERE {where}')
        await bot.db.commit()
        async with bot.db.execute(f'SELECT * FROM {table}') as cursor:
            async for row in cursor:
                print(row)
        await bot.db.close()

    async def insert(table, column, value):
        bot.db = await aiosqlite.connect('storage.db')
        await bot.db.execute(f'INSERT INTO "{table}" ("{column}") VALUES ("{value}")')
        await bot.db.commit()
        async with bot.db.execute(f'SELECT * FROM {table}') as cursor:
            async for row in cursor:
                print(row)
        await bot.db.close()

    async def update(table, column, value, where):
        bot.db = await aiosqlite.connect('storage.db')
        await bot.db.execute(f'UPDATE {table} SET {column} = "{value}" WHERE {where}')
        await bot.db.commit()
        async with bot.db.execute(f'SELECT * FROM {table}') as cursor:
            async for row in cursor:
                print(row)
        await bot.db.close()
    #NOTE - DB section end

    async def fetchAddress(guildId):
        where = (f'discordServerId = {guildId}')
        serverAddress = serverAddress = await select(column='aternosServerAddress', table='ServersAddresses', where=str(where))
        serverAddress = str(serverAddress)[1:-1]
        return serverAddress

    @bot.event
    async def on_ready():
        print(f"{bot.user} is ready and online!")

    @bot.event
    async def on_guild_join(guild):
        general = find(lambda x: x.name == 'general',  guild.text_channels)
        try:
            await insert(table='ServersAddresses', column='discordServerId', value=guild.id)
            if general and general.permissions_for(guild.me).send_messages:
                await general.send('Hello {}!'.format(guild.name))
            print('Discord server id: '+str(guild.id))
        except aiosqlite.Error as e:
            if general and general.permissions_for(guild.me).send_messages:
                await general.send('Hello! Server id issue :(\n\nDM developer please!')
            print('Discord server id: '+str(guild.id))
            print('Error: '+str(e))
        

    @bot.command(description="Sends the bot's latency.")
    async def ping(ctx):
        title = 'Aternos Server Controller'
        descr = ('Pong! Latency is '+str(bot.latency))
        embed = createEmbed(title, descr)
        await ctx.respond(embed=embed)

    @bot.command(description='Sets the Aternos server address.')
    async def set(ctx, address):
        where = (f'discordServerId = {ctx.guild.id}')
        await update(table='ServersAddresses', column='aternosServerAddress', value=str(address), where=str(where))
        embed = createEmbed(title='Server address set correctly!')
        await ctx.respond(embed=embed)

    @bot.command(description='Shows current Aternos server address.')
    async def view(ctx):
        serverAddress = await fetchAddress(ctx.guild.id)
        if serverAddress == 'on':
            serverAddress = 'Address not set, use "/set" to set your aternos server address!'
        embed = createEmbed(title='The current server address is: ', description=serverAddress)
        await ctx.respond(embed=embed)

    @bot.command(description='Shows helpful commands list.')
    async def help(ctx):
        embed=discord.Embed(title="Commands List", url="https://github.com/Ho3pLi/AternosDiscordBot", description="Just a list of commands to use ASC!", color=0x00fbff)
        embed.set_author(name="Made by Ho3pLi", url="https://github.com/Ho3pLi", icon_url="https://i.ibb.co/kJYfNm5/61387309.jpg")
        embed.set_thumbnail(url="https://i.ibb.co/ZJDRCW1/226-2267191-minecrafts-command-block-is-a-psuedo-programming-language.png")
        embed.add_field(name="/view", value="Checks current Server Address", inline=False)
        embed.add_field(name="/set", value="Set your Server Address", inline=False)
        embed.add_field(name="/start", value="Starts your server", inline=False)
        embed.add_field(name="/stop", value="Stops your server", inline=False)
        embed.add_field(name="/status", value="Check your server current status", inline=False)
        embed.add_field(name="/info", value="Provides general info of your Aternos server.", inline=False)
        embed.add_field(name="/playerlist", value="Shows a list of current online players.", inline=False)
        embed.add_field(name="/onlineplayers", value="Shows number of current online players.", inline=False)
        embed.add_field(name="/help", value="Shows this message", inline=False)
        embed.add_field(name="/ping", value="Sends the bot's latency.", inline=False)
        embed.set_footer(text="For any issues DM Ho3pLi#4932")
        await ctx.respond(embed=embed)

    @bot.command(description='Starts your Aternos server.')
    async def start(ctx):
        serverAddress = await fetchAddress(ctx.guild.id)
        status = serverStatus(serverAddress)
        if status == 'offline':
            runServer()
            embed = createEmbed(title='Server online', description='Server starting..')
            await ctx.respond(embed=embed)
        elif status == 'loading' or status == 'preparing':
            embed = createEmbed(title='Server online', description='Server starting..')
            await ctx.respond(embed=embed)
        elif status == 'online':
            embed = createEmbed(title='Server online', description='Server online')
            await ctx.respond(embed=embed)

    @bot.command(description='Shows current Aternos server status.')
    async def status(ctx):
        serverAddress = await fetchAddress(ctx.guild.id)
        status = serverStatus(serverAddress)
        embed = createEmbed(title='The server is:', description=status)
        await ctx.respond(embed=embed)

    @bot.command(description='Stops your Aternos server.')
    async def stop(ctx):
        serverAddress = await fetchAddress(ctx.guild.id)
        status = serverStatus(serverAddress)
        title = 'Server status: '+status
        if status == 'online':
            stopServer()
            embed = createEmbed(title, description='Server shutting down..')
            await ctx.respond(embed=embed)
        elif status == 'loading' or status == 'preparing':
            embed = createEmbed(title, description='Server starting, you can\'t stop it now.\nTry when the server is online!')
            await ctx.respond(embed=embed)
        elif status == 'offline':
            embed = createEmbed(title, description='Server offline')
            await ctx.respond(embed=embed)

    @bot.command(description='Shows number of current online players.')
    async def onlineplayers(ctx):
        serverAddress = await fetchAddress(ctx.guild.id)
        status = serverStatus(serverAddress)
        if status == 'online':
            rs = getOnlinePlayers(serverAddress)
            embed = createEmbed(title='Current number of players', description=str(rs))
            await ctx.respond(embed=embed)
        else:
            embed = createEmbed(title='The server is offline!')
            await ctx.respond(embed=embed)
    
    @bot.command(description='Shows a list of current online players.')
    async def playerlist(ctx):
        serverAddress = await fetchAddress(ctx.guild.id)
        rs = getPlayerList(serverAddress)
        embed = createEmbed(title='Player list', description='\n'.join(rs))
        await ctx.respond(embed=embed)

    @bot.command(description='Provides general info of your Aternos server.')
    async def info(ctx):
        serverAddress = await fetchAddress(ctx.guild.id)
        statusTitle = 'Server status'
        status = serverStatus(serverAddress)
        title = 'General info'
        onlinePlayersTitle = 'Online Players'
        onlineP = getOnlinePlayers(serverAddress)
        playerListTitle = 'Player List'
        playerList = getPlayerList(serverAddress)
        playerListProcessed = '\n'.join(playerList)
        embed = createEmbed(title, '', statusTitle, status, onlinePlayersTitle, onlineP, playerListTitle, playerListProcessed)
        await ctx.respond(embed=embed)

    asyncio.get_event_loop().run_until_complete(dbSetup())
    bot.run(os.getenv('DISCORD_TOKEN'))

#NOTE - Aternos section

def serverStatus(serverAddress) -> str:
    aternos = Client.from_hashed('Ho3pLi', '2f37ce8d68dea0676ba16ea100ba87e2')

    servers = aternos.list_servers()
    myServer = None

    for server in servers:
        if server.address == serverAddress:
            myServer = server
    
    return myServer.status

def runServer(serverAddress):
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

def stopServer(serverAddress):
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

def getOnlinePlayers(serverAddress):
    aternos = Client.from_hashed('Ho3pLi', '2f37ce8d68dea0676ba16ea100ba87e2')

    servers = aternos.list_servers()

    myServer = None

    for server in servers:
        if server.address == serverAddress:
            myServer = server
        
    return ('Online: '+str(myServer.players_count)+' of '+str(myServer.slots))

def getPlayerList(serverAddress):
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