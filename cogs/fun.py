import functions
import requests
import discord
import json
import random
import os
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType
from discord.ext import commands
from discord.ext import menus
from discord.ext import owoify


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.session_message = {}
        self.buttons = {
            "default": {
                "aa": [
                    [
                        Button(style=ButtonStyle.red, label="Redo")
                    ],
                ]
            },
            "disabled": {
                "aa": [
                    [
                        Button(style=ButtonStyle.red, label="Redo", disabled=True)
                    ]
                ]
            }
        }

    # CMD-ADJECTIVEANIMAL
    @commands.command(aliases=['aa'])
    async def adjectiveanimal(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        adjectives = [
            "Polite",
            "Sizzling",
            "Joyful",
            "Zany",
            "Selfish",
            "Sleepy",
            "Agreeable",
            "Friendly",
            "Wise",
            "Helpful",
            "Pervasive",
            "Hasty",
            "Odd",
            "Enthusiastic",
            "Slow",
            "Lazy",
            "Cheerful",
            "Unusual",
            "Shining",
            "Busy",
            "Calm",
            "Nice",
            "Enchanting",
            "Icy",
            "Luminous",
            "Hasty",
            "Nimble",
            "Majestic",
            "Alert",
            "Aromatic",
            "Rapid",
            "Loyal",
            "Aimless",
            "Majestic",
            "Friendly",
            "Plucky",
            "Grimy",
            "Nimble",
            "Strict",
            "Pleasant",
            "Wild"
        ]

        animals = [
            "Emu",
            "Quail",
            "Possum",
            "Viper",
            "Shark",
            "Snail",
            "Chimpanzee",
            "Giraffe",
            "Gorilla",
            "Lizard",
            "Piranha",
            "Jellyfish",
            "Squirrel",
            "Scorpion",
            "Hippo",
            "Caterpillar",
            "Alpaca",
            "Otter",
            "Tortoise",
            "Panther",
            "Koala",
            "Bat",
            "Frog",
            "Buffalo",
            "Squirrel",
            "Vulture",
            "Urchin",
            "Newt",
            "Eagle",
            "Ostrich",
            "Marmoset",
            "Chameleon",
            "Kitten",
            "Monkey",
            "Cheetah",
            "Walrus",
            "Badger"
        ]

        adjective = random.choice(adjectives)
        animal = random.choice(animals)

        name = adjective + animal

        accounts_with_name = 0
        response = requests.get(f"https://accounts.rec.net/account/search?name={name}")
        if response.ok:
            accounts = response.json()
            for account in accounts:
                if name.casefold() in account['username'].casefold():
                    accounts_with_name += 1

            if accounts_with_name == 50:
                accounts_with_name = "50+"
        else:
            accounts_with_name = 0

        embed = discord.Embed(
            title="Your adjective animal name:",
            description=f"**{name}**\nAccounts with that username: `{accounts_with_name}`",
            colour=discord.Colour.orange()
        )

        embed = functions.embed_footer(ctx, embed)

        m = await ctx.send(
            embed=embed,
            components=self.buttons['default']['aa']
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(components=self.buttons['disabled']['aa'])

        if res.component.label == "Redo":
            await m.edit(
                components=self.buttons['disabled']['aa']
            )
            await self.adjectiveanimal(ctx)

    # CMD-CRINGENAMECHECK
    @commands.command(aliases=["cnc"])
    @commands.check(functions.beta_tester)
    async def cringenamecheck(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)
        if account:
            embed = functions.default_embed()

            cringe_check_list = functions.load("cringe_word_list.json")
            cringe_score = 0
            cringe_rating = {
                0: "Not cringe!",
                1: "Maybe a little cringe?",
                2: "Little cringe.",
                3: "A bit cringe!",
                4: "Cringe!",
                5: "Quite cringe!",
                6: "Very cringe!",
                7: "Super cringe!",
                8: "Incredibly cringe!",
                9: "Ludicrously cringe!",
                10: "THE CRINGIEST!"
            }

            display_name = functions.id_to_display_name(account['account_id'])
            cringe_words = [ele for ele in cringe_check_list if (ele.casefold() in display_name.casefold())]
            cringe_score = len(cringe_words) * 2

            for char in display_name:
                if not char.isalpha():
                    cringe_score += 1
                    cringe_words.append(char)

            if cringe_score > 10:
                cringe_score = 10

            embed.add_field(name=f"{account['username']}'s display name:", value=f"```{display_name}```")
            embed.add_field(name="Cringe score", value=f"`{cringe_score}` ({cringe_rating[cringe_score]})",
                            inline=False)

            flags = ""
            for flag in cringe_words:
                flags += f"`{flag}`, "

            if flags:
                embed.add_field(name="Flags",
                                value=f"||{flags}||\nThis command is just for fun, and not meant to shame anybody!",
                                inline=False)

            pfp = functions.id_to_pfp(account['account_id'], True)
            embed.set_author(name=f"🔗 {account['username']}'s profile",
                             url=f"https://rec.net/user/{account['username']}", icon_url=pfp)
        else:
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(embed=embed)

    @cringenamecheck.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")

            await ctx.send(embed=embed)
        else:
            pass

    # CMD-BOXSIM
    @commands.command(aliases=['bsim'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def boxsim(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        global reward_instance  # I hate doing this, but it works.
        reward_instance[ctx.author.id] = {
            "rewards": await reward_selection(3, [], False)}
        menu = RewardSelection()
        await menu.start(ctx)


econ_path = "/root/RecNetBot/Economy"
reward_instance = {}


async def reward_selection(amount=3, categories=[], dupes=False):
    is_token_reward = False
    rewards = []
    for x in range(amount):
        item = None
        while not item:
            item = await random_drop()
            if (await get_id(item['name']) not in rewards) or dupes:  # Check for duplicate
                # No duplicate tokens
                if item['category'] == "tokens":
                    if is_token_reward:
                        item = None
                        continue
                    else:
                        is_token_reward = True
                # Add reward to list
                rewards.append(await get_id(item['name']))
            else:
                item = None
    return rewards


async def get_id(item_name):
    ITEMS = await return_drops()

    old_category = ""
    for item in ITEMS:
        if old_category != item['category']:
            id = 0
            old_category = item['category']

        if item['name'].lower() == item_name.lower():
            item_id = f"{item['category']}:{id}"
            print(f"Found item with name {item_name}! Id: {item_id}")
            return item_id

        id += 1
    return False


async def random_drop():
    chance = random.randint(1, 300)
    if chance > 200:
        # 1 Star
        item_pool = await get_items_of_rarity(1)
    elif chance > 80:
        # 2Star
        item_pool = await get_items_of_rarity(2)
    elif chance > 30:
        # 3 Star
        item_pool = await get_items_of_rarity(3)
    elif chance > 2:
        # 4 Star
        item_pool = await get_items_of_rarity(4)
    else:
        # 5 Star
        item_pool = await get_items_of_rarity(5)

    item = random.choice(item_pool)
    print(f"Random drop - {item['name']} - {chance}% - rarity {item['rarity']}")
    return item


async def get_items_of_rarity(rarity=1):
    ITEMS = await return_drops()
    item_pool = []
    for item in ITEMS:
        if item['rarity'] == rarity:
            item_pool.append(item)
    print(f"Returned items of rarity {rarity}, count {len(item_pool)}")
    return item_pool


async def return_drops(category=None):
    global econ_path
    items = []
    if category:
        try:
            with open(f'{econ_path}/items/{category}.json', "r") as json_file:
                items = json.load(json_file)
        except:
            with open(f'{econ_path}/cosmetics/{category}.json', "r") as json_file:
                items = json.load(json_file)
    else:
        for file in os.listdir(f"{econ_path}/items/"):
            if file.endswith(".json"):
                with open(f'{econ_path}/items/{file}', "r") as json_file:
                    items += json.load(json_file)
        for file in os.listdir(f"{econ_path}/cosmetics/"):
            if file.endswith(".json"):
                with open(f'{econ_path}/cosmetics/{file}', "r") as json_file:
                    items += json.load(json_file)

    return items


async def parse_id(item_id):
    parsed_id = item_id.split(":")
    return {"category": parsed_id[0], "index": int(parsed_id[1])}


async def get_item_data(item_id):
    parsed_id = await parse_id(item_id)

    print(parsed_id)

    ITEMS = await return_drops(parsed_id['category'])

    return ITEMS[parsed_id['index']]


class RewardSelection(menus.Menu):
    global reward_instance

    async def send_initial_message(self, ctx, channel):
        reward_instance[self._author_id]['ctx'] = ctx

        embed = discord.Embed(
            colour=0x2f3136,
            title="Choose a reward!"
        )

        rewards = reward_instance[self._author_id]['rewards']

        for item in rewards:
            item_data = await get_item_data(item)

            stars = "\n"
            if item_data['category'] != "tokens":
                # Rarity string
                for i in range(item_data['rarity']):
                    stars += "<:RRStar:825357537209090098> "
            if stars == "\n":
                stars = ""

            embed.add_field(name=f"{item_data['emoji_icon']} {item_data['name']}",
                            value=f"<:RRtoken:825288414789107762> `{item_data['tokens']}`{stars}",
                            inline=True)

        # embed.add_field(name="DEBUG", value=reward_instance.keys())
        # embed.set_footer(text=f"Author id: {self._author_id}")

        box_img_url = "https://i.imgur.com/SBxexI1.png"

        embed.set_thumbnail(url=box_img_url)
        embed = functions.embed_footer(ctx, embed)

        return await channel.send(embed=embed)

    async def update_menu(self, reward):
        global reward_instance
        item_id = reward_instance[self._author_id]['rewards'][reward]
        item = await get_item_data(item_id)
        ctx = reward_instance[self._author_id]['ctx']

        if item['rarity'] == 5:
            color = discord.Colour.orange()
        elif item['rarity'] == 4:
            color = discord.Colour.purple()
        elif item['rarity'] == 3:
            color = discord.Colour.blue()
        elif item['rarity'] == 2:
            color = discord.Colour.green()
        else:
            color = discord.Colour.dark_gray()

        embed = discord.Embed(
            colour=color,
            title="Reward chosen!"
        )

        stars = "\n"
        if item['category'] != "tokens":
            # Rarity string
            for i in range(item['rarity']):
                stars += "<:RRStar:825357537209090098> "
            if stars == "\n":
                stars = ""
            else:
                stars += "\n"

        embed.add_field(name=f"{item['emoji_icon']} {item['name']}",
                        value=f"<:RRtoken:825288414789107762> `{item['tokens']}`{stars}\n",
                        inline=False)
        embed.set_footer(text=f"Given to {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=item['img_url'])

        await self.message.edit(embed=embed)
        reward_instance.pop(self._author_id, None)

        self.stop()

    @menus.button('1️⃣')
    async def reward_one(self, payload):
        await self.update_menu(0)

    @menus.button('2️⃣')
    async def reward_two(self, payload):
        await self.update_menu(1)

    @menus.button('3️⃣')
    async def reward_three(self, payload):
        await self.update_menu(2)


def setup(client):
    client.add_cog(Fun(client))
