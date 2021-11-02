import discord
import os
import functions
from discord.ext.commands import CommandNotFound
from discord.ext import commands

config = functions.load("config.json")

client = discord.Client()

# Setting up
#intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)
#client = commands.Bot(command_prefix = '.', intents = intents, help_command=None, case_insensitive=True)
client = commands.Bot(command_prefix=config['prefix'], help_command=None, case_insensitive=True)


# When bot online
@client.event
async def on_ready():
    print("Bot is ready!")
    print('Servers connected to:')
    print(f"Servers: {len(client.guilds)}")
    for guild in client.guilds:
        print(f"-{guild.name}")
        print(f"{guild.owner}")
        print(f"Members: {len(guild.members)}\n")
    await client.change_presence(status=discord.Status.online, activity=discord.Game(".help | bit.ly/RecNetBot"))


@client.event
async def on_command_error(ctx,error):
    if isinstance(error, CommandNotFound):
        return


# Commands
@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {int(client.latency*1000)}!')


@client.command()
@commands.check(functions.is_it_me)
async def unload(ctx, extension):
    try:
        client.unload_extension(f"cogs.{extension}")
        await ctx.send(f"`{extension}` unloaded!")
    except:
        await ctx.send(f"`{extension}` couldn't be unloaded!")

@client.command()
@commands.check(functions.is_it_me)
async def load(ctx, extension):
    try:
        client.load_extension(f"cogs.{extension}")
        await ctx.send(f"`{extension}` loaded!")
    except:
        await ctx.send(f"`{extension}` couldn't be loaded!")

@client.command()
@commands.check(functions.is_it_me)
async def reload(ctx, extension):
    try:
        client.unload_extension(f"cogs.{extension}")
        client.load_extension(f"cogs.{extension}")
        await ctx.send(f"`{extension}` reloaded!")
    except:
        await ctx.send(f"`{extension}` couldn't be loaded!")

@client.command(aliases=['rall'])
@commands.check(functions.is_it_me)
async def reloadall(ctx):
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            client.unload_extension(f"cogs.{filename[:-3]}")
            client.load_extension(f"cogs.{filename[:-3]}")
    await ctx.send("Cogs reloaded!")

@client.command()
@commands.check(functions.is_it_me)
async def guilds(ctx):
    string = f"**Servers:** {len(client.guilds)}\n\n"
    for guild in client.guilds:
        #string += f"-{guild.name}\n{guild.owner}\n**Members:** {len(guild.members)}\n"
        string += f"-{guild.name}\n"
    await ctx.send(string)


def return_guild_count():
    return len(client.guilds)

# Load cogs
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

# token
client.run(config['token'])
