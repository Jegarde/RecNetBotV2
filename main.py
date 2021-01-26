import discord
import os
import keep_alive
import functions
from discord.ext import commands

client = discord.Client()

# Setting up
intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)
client = commands.Bot(command_prefix = '.', intents = intents, help_command=None)


# When bot online
@client.event
async def on_ready():
    print("Bot is ready!")
    print('Servers connected to:')
    print(f"Servers: {len(client.guilds)}")
    for guild in client.guilds:
        print(f"-{guild.name}")
    await client.change_presence(status=discord.Status.idle, activity=discord.Game("Under development."))


# Commands
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

    @client.command()
    @commands.check(functions.is_it_me)
    async def reloadall(ctx):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                client.unload_extension(f"cogs.{filename[:-3]}")
                client.load_extension(f"cogs.{filename[:-3]}")
        await ctx.send(f"Cogs reloaded!")

        
# Load cogs
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

#keep it alive
keep_alive.keep_alive()


# token
client.run(os.getenv('TOKEN'))