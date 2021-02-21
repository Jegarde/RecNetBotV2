import functions
import discord
from discord.ext import commands

class Search(commands.Cog):
    def __init__(self, client):
        self.client = client

    # SEARCH COMMANDS

    #CMD-EVENTSEARCH
    @commands.command(aliases=["es"])
    @commands.check(functions.beta_tester)
    async def eventsearch(self, ctx, word):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        keyword = str(word)
        if len(keyword) < 2:
            embed = functions.error_msg(ctx, "Keyword must be at least 2 characters long!")
            await ctx.send(embed=embed)
        else:
            events_found = functions.event_search(keyword)

            embed=discord.Embed(
                colour=discord.Colour.orange(),
                title = f"Events found with keyword \"{keyword}\"",
            )

            events = 0
            if events_found:
                for event in events_found:
                    if (functions.contains_word(event['Name'], keyword) or functions.contains_word(event['Description'], keyword)):
                        description = event['Description']
                        if not description:
                            description = "None"

                        events += 1

                        embed.add_field(name=event['Name'], value=f"**[\"{event['Name']}\"](https://rec.net/event/{event['PlayerEventId']})** | [`{functions.id_to_display_name(event['CreatorPlayerId'])}`](https://rec.net/user/{functions.id_to_username(event['CreatorPlayerId'])})```{description}```👥 Attending: `{event['AttendeeCount']}`\n\n~~~~~~~~~~", inline=False)

            if not events:
                embed.add_field(name="None!", value=f"Couldn't find any event that contains the word `{keyword}`", inline=False)
                

            functions.embed_footer(ctx, embed) # get default footer from function
            await ctx.send(embed=embed)

    @eventsearch.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in a word to search!")
            
            await ctx.send(embed=embed)
        else:
            pass

def setup(client):
    client.add_cog(Search(client))