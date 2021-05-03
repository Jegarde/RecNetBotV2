import functions
import requests
import discord
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Admin COMMANDS
    @commands.command(aliases=['acw'])
    @commands.check(functions.is_it_me)
    async def add_cringe_word(self, ctx, word=None):
        if not word:
            return await ctx.send("Include in a word maybe???")

        cringe_words = functions.load("cringe_word_list.json")
        if word not in cringe_words:
            cringe_words.append(word)
            functions.save("cringe_word_list.json", cringe_words)
            await ctx.send(f"`{word}` added to cringe word list!")
        else:
            await ctx.send(f"`{word}` in cringe word list already!")


    @commands.command(aliases=['rcw'])
    @commands.check(functions.is_it_me)
    async def remove_cringe_word(self, ctx, word=None):
        if not word:
            return await ctx.send("Include in a word maybe???")

        cringe_words = functions.load("cringe_word_list.json")
        try:
            cringe_words.remove(word)
            functions.save("cringe_word_list.json", cringe_words)
            await ctx.send(f"`{word}` removed from cringe word list!")
        except:
            await ctx.send(f"`{word}` not in cringe word list!")


    @commands.command(aliases=['cw'])
    @commands.check(functions.is_it_me)
    async def cringe_words(self, ctx):
        cringe_words = functions.load("cringe_word_list.json")

        words = ""
        for word in cringe_words:
            words += f"`{word}`, "
        await ctx.send(words)


def setup(client):
    client.add_cog(Admin(client))
