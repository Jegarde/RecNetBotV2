import functions
import discord
import random
from discord.ext import menus
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType
from main import return_guild_count


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.session_message = {}
        DiscordComponents(client)
        self.main_buttons = [
            [
                Button(style=ButtonStyle.red, label="Utility", emoji="🛠️"),
                Button(style=ButtonStyle.red, label="Random", emoji="❓"),
                Button(style=ButtonStyle.red, label="Menus", emoji="📟"),
            ],
            [
                Button(style=ButtonStyle.red, label="CV2", emoji="⚙"),
                Button(style=ButtonStyle.red, label="Fun", emoji="😹"),
                Button(style=ButtonStyle.red, label="API", emoji="📲")
            ],
            [
                Button(style=ButtonStyle.red, label="Legacy", emoji="👾"),
                Button(style=ButtonStyle.red, label="Other", emoji="📖")
            ],
            [
                Button(style=ButtonStyle.URL, label="Invite Bot", url="https://discord.com/api/oauth2/authorize?client_id=788632031835324456&permissions=322624&scope=bot"),
                Button(style=ButtonStyle.URL, label="Discord", url="https://discord.gg/GPVdhMa2zK")
            ]
        ]

        self.main_buttons_disabled = [
            [
                Button(style=ButtonStyle.red, label="Utility", emoji="🛠️", disabled=True),
                Button(style=ButtonStyle.red, label="Random", emoji="❓", disabled=True),
                Button(style=ButtonStyle.red, label="Menus", emoji="📟", disabled=True),
            ],
            [
                Button(style=ButtonStyle.red, label="CV2", emoji="🔎", disabled=True),
                Button(style=ButtonStyle.red, label="Fun", emoji="😹", disabled=True),
                Button(style=ButtonStyle.red, label="API", emoji="📲", disabled=True)
            ],
            [
                Button(style=ButtonStyle.red, label="Legacy", emoji="👾", disabled=True),
                Button(style=ButtonStyle.red, label="Other", emoji="📖", disabled=True)
            ],
            [
                Button(style=ButtonStyle.URL, label="Invite Bot",
                       url="https://discord.com/api/oauth2/authorize?client_id=788632031835324456&permissions=322624&scope=bot"),
                Button(style=ButtonStyle.URL, label="Discord", url="https://discord.gg/GPVdhMa2zK")
            ]
        ]

        self.menu_button = [
            [
                Button(style=ButtonStyle.red, label="Main"),
            ]
        ]

        self.menu_button_disabled = [
            [
                Button(style=ButtonStyle.red, label="Main", disabled=True),
            ]
        ]
    @commands.command()
    @commands.check(functions.beta_tester)
    async def help(self, ctx, menu=None):
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session
        if menu:
            menu = menu.lower()
        main = False
        if menu == "utility":
            embed = discord.Embed(
                colour=discord.Colour.orange(),
                title="🛠️ Utility commands",
            )
            embed.add_field(name="👤 Accounts",
                            value="`stats`, `creatorstats`, `topsubscribed`, `topcreators`, `bio`, `pfp`, `banner`, "
                                  "`profile`, `junior`, `date`, `nickname`, `platforms`, `level`, `older`",
                            inline=False)

            embed.add_field(name="🖼️ Images",
                            value="`photos`, `feed`, `latest`, `latestinby`, `latestwith` `latestfeed`, `oldest`, "
                                  "`oldestinby`, `oldestwith`, `oldestfeed`, `frontpage`, `takenin`, `takenof`, "
                                  "`takenofin`, `together`, `cheers`, `comments`, `photostats`, `sortby`, "
                                  "`bookmarked`, `infrontpage`, `gap`",
                            inline=False)

            embed.add_field(name="🚪 Rooms", value="`room`, `roles`, `roomsby`, `featured`, `placement`",
                            inline=False)

            embed.add_field(name="🗓️ Events", value="`eventsearch`, `latestevents`, `eventsby`, `eventsbyin`, `eventsin`",
                            inline=False)

            embed.add_field(name="<:RRQuestion:803587583187746847> Other", value="`apistatus`, "
                                                                                 "`shortcuts`", inline=False)
        elif menu == "other":
            embed = discord.Embed(
                colour=discord.Colour.orange(),
                title="📖 Other commands",
                description="`doc`, `invite`, `cringebios`"
            )
        elif menu == "random":
            embed = discord.Embed(
                colour=discord.Colour.orange(),
                title="<:RRQuestion:803587583187746847> \"Random\" commands",
            )

            embed.add_field(name="🖼️ Images", value="`randomimg`, `randomimgof`, `randomimgofin`,`randomimgby`, "
                                                     "`randomimgbyin`, `randomimgin`, `randompfp`", inline=False)

            embed.add_field(name="📜 Bios", value="`randombio`, `cringebio`, `fastrandombio`", inline=False)

            embed.add_field(name="<:RRQuestion:803587583187746847> Other", value="`randomaccount`, `randomroom`, "
                                                                                 "`randomevent`, `randomloadscreen`",
                            inline=False)

        elif menu == "cv2":
            embed = discord.Embed(
                colour=discord.Colour.orange(),
                title="<:cv2:856865728527204353> Circuits V2 commands",
            )
            embed.add_field(name="<:cv2:856865728527204353> Chips", value="`chips`, `chip`, `cvresources`", inline=False)
        elif menu == "api":
            embed = discord.Embed(
                colour=discord.Colour.orange(),
                title="📲 API commands",
            )
            embed.add_field(name="👤 Accounts", value="`accountdata`, `accountid`", inline=False)

            embed.add_field(name="🚪 Rooms", value="`roomdata`, `roomid`", inline=False)

            embed.add_field(name="🖼️ Images", value="`imageid`", inline=False)

        elif menu == "menus":
            embed = discord.Embed(
                colour=discord.Colour.orange(),
                title="📟 Menu commands",
                description="These commands utilize the slick menu system! They can also be found in other "
                            "categories. "
            )
            embed.add_field(name="📟 Menus", value="`frontpage`, `photos`, `feed`, `sortby`, `together`, `takeninby`, "
                                                   "`takenofby`, `takenofin`", inline=False)
        elif menu == "legacy":
            embed = discord.Embed(
                colour=discord.Colour.orange(),
                title="👾 Legacy commands",
                description="These commands are the original versions of some reworked commands."
            )
            embed.add_field(name="👾 Legacy", value="`lfrontpage`, `lsortby`, `ltogether`, `ltakenin`, `ltakenof`, "
                                                    "`ltakenofin`", inline=False)
        elif menu == "economyy":
            embed = discord.Embed(
                colour=discord.Colour.orange(),
                title="<:RRtoken:825288414789107762> Economy commands",
                description="Economy is under development."
            )
            embed.add_field(name="<:RRtoken:825288414789107762> Economy", value="`econprofile (ep)`, `econstats ("
                                                                                "estats)`, `inventory (inv)`, `play`, "
                                                                                "`boxes`, `unbox (ub)` `buy`, `gift`, "
                                                                                "`sell`, `sellall`, `badges`, "
                                                                                "`daily`, `beg`, `leaderboard`, "
                                                                                "`boosters`, `use`, `upgrade`, "
                                                                                "`mirror`, `equip`, `unequip`, "
                                                                                "`item`", inline=False)
        elif menu == "fun":
            embed = discord.Embed(
                colour=discord.Colour.orange(),
                title="😹 Fun commands"
            )
            embed.add_field(name="🎮 Minigames", value="`boxsim`", inline=False)
            embed.add_field(name="📑 Checks", value="`cringebiocheck`, `cringenamecheck`, `selfcheers`", inline=False)
            embed.add_field(name="<:stare:796100757358510081> Other", value="`owoify`", inline=False)
            embed.add_field(name="<:wholesome:796100757354053653> Other", value="`adjectiveanimal`", inline=False)
        else:
            embed = discord.Embed(
                colour=discord.Colour.orange(),
                title="RecNetBot Command List"
            )

            embed.add_field(name="🛠️ Utility", value="`.help utility`")
            embed.add_field(name="<:RRQuestion:803587583187746847> \"Random\"", value="`.help random`")
            embed.add_field(name="📟 Menus", value="`.help menus`")
            embed.add_field(name="<:cv2:856865728527204353> CV2", value="`.help cv2`")
            embed.add_field(name="😹 Fun", value="`.help fun`")
            embed.add_field(name="📲 API", value="`.help api`")
            embed.add_field(name="👾 Legacy", value="`.help legacy`")
            embed.add_field(name="📖 Other", value="`.help other`")
            # embed.add_field(name="<:RRtoken:825288414789107762> Economy (Early Alpha)", value="`.help economy`")

            rnb_stats = {'TotalCount': None, 'GuildCount': len(self.client.guilds)}

            embed.add_field(name="Other",
                            value=f"[Invite bot](https://discord.com/api/oauth2/authorize?client_id"
                                  f"=788632031835324456&permissions=322624&scope=bot) | [Discord]("
                                  f"https://discord.gg/GPVdhMa2zK)\n<:discord:803539862435135510> Server count: `"
                                  f"{rnb_stats['GuildCount']}`",
                            inline=False)
            main = True

        functions.embed_footer(ctx, embed)
        if main:
            m = await ctx.send(embed=embed, components=self.main_buttons)
        else:
            m = await ctx.send(embed=embed, components=self.menu_button)

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            if main:
                return await m.edit(components=self.main_buttons_disabled)
            else:
                return await m.edit(components=self.menu_button_disabled)

        if main:
            """
            await m.edit(
                components=self.main_buttons_disabled
            )
            """
            await m.delete()
            await self.help(ctx, res.component.label)

        else:
            """
            await m.edit(
                components=self.menu_button_disabled
            )
            """
            await m.delete()
            await self.help(ctx)



def setup(client):
    client.add_cog(Help(client))
