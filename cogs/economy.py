import functions
import json
import discord
from discord.ext import commands
from discord.ext import menus
import random
import os

reward_instance = {}
inventories = {}

def return_drops(category=False):
    items = []
    if category:
        with open(f'/home/runner/RecNetBotV2/items/{category}.json') as json_file:
            items = json.load(json_file)
    else:
        for file in os.listdir("/home/runner/RecNetBotV2/items/"):
            print(file)
            if file.endswith(".json"):
                with open(f'/home/runner/RecNetBotV2/items/{file}') as json_file:
                    items += json.load(json_file)

    return items


def random_drop():
    chance = random.randint(1, 100)
    print(str(chance) + "%")
    if chance > 80:
        # Film
        item_pool = return_drops("film")
    elif chance > 20:
        # Pizza / Donuts / Pretzels / Root Beer
        item_pool = return_drops("pizza") + return_drops("donuts") + [return_drops("other")[0]] + [return_drops("drinks")[0]]
    elif chance > 15:
        # Popcorn / KO
        item_pool = return_drops("ko") + [return_drops("other")[1]]
    elif chance > 10:
        # Cake
        item_pool = return_drops('cake')
    elif chance > 5:
        # 10 / 25 Tokens
        item_pool = [return_drops("tokens")[0]] + [return_drops("tokens")[1]]
    elif chance > 2:
        # 100 Tokens
        item_pool = [return_drops("tokens")[2]]
    else:
        # Bubbly
        item_pool = [return_drops("drinks")[1]]
    
    item = random.choice(item_pool)
    return item
   
async def reward_selection(amount=3):
    is_token_reward = False
    rewards = []
    for x in range(amount):
        item = None
        while not item: 
            item = random_drop()
            if item not in rewards: # Check for duplicate
                # No duplicate tokens
                if item['category'] == "tokens":
                    if is_token_reward:
                        item = None
                        continue
                    else:
                        is_token_reward = True
                # Add reward to list
                rewards.append(item)
            else: item = None
        #print(f"You got {item['name']}! It's worth {item['tokens']} tokens!")
    return rewards
    #print(rewards)

async def get_inventory(user_id):
    global inventories

    if user_id not in inventories.keys():
        inventories[user_id] = {}

    return inventories[user_id]

async def add_to_inventory(user_id, item_index, amount):
    global inventories
    await get_inventory(user_id)

    user_id, item_index, amount = int(user_id), int(item_index), int(amount)

    ITEMS = return_drops()
    item = ITEMS[int(item_index)]
    print(item)

    if item['category'] == "tokens":
        try:
            inventories[user_id]['tokens'] += item['tokens']
        except:
            inventories[user_id]['tokens'] = item['tokens']
    elif item['name'] not in inventories[user_id]:
        print("Item not in inventory yet!")
        inventories[user_id][item['name']] = {'amount': amount}
    else:
        print("Item in inventory!")
        inventories[user_id][item['name']]['amount'] += amount

    print(inventories)


async def set_tokens(user_id, amount):
    global inventories
    user_id, amount = int(user_id), int(amount)
    await get_inventory(user_id)

    inventories[user_id]['tokens'] = amount


class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['rbox'])
    #@commands.cooldown(3, 86400, commands.BucketType.user)
    #@commands.check(functions.is_it_me)
    async def randombox(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        global reward_instance # I hate doing this, but it works.
        reward_instance[ctx.author.id] = {"rewards": await reward_selection(3)}
        menu = RewardSelection()
        await menu.start(ctx)

    @randombox.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = functions.error_msg(ctx, f"All daily boxes opened! Try again in {round(error.retry_after/3600)}h")
                
            await ctx.send(embed=embed)
        else:
            pass

    @commands.command()
    @commands.check(functions.is_it_me)
    async def give(self, ctx, mention: discord.User, item_index, amount):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        await add_to_inventory(mention.id, item_index, amount)


    @commands.command()
    @commands.check(functions.is_it_me)
    async def settokens(self, ctx, mention: discord.User, amount):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        await set_tokens(mention.id, amount)


    @commands.command(aliases=['inv'])
    async def inventory(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        global inventories # I hate doing this, but it works.

        await get_inventory(ctx.author.id)

        auth_inv = inventories[ctx.author.id]

        inventory_string = ""
        for item in auth_inv:
            if item == "tokens":
                continue
            inventory_string += f"{item}: `{auth_inv[item]['amount']}`\n"

        embed = discord.Embed(
            colour= discord.Colour.orange(),
            title = "Inventory",
            description = inventory_string
        )

        if not "tokens" in auth_inv.keys():
            auth_inv['tokens'] = 0
        embed.add_field(name="Tokens", value=f"<:RRtoken:825288414789107762> `{auth_inv['tokens']}`", inline=False)

        print(auth_inv)
        await ctx.send(embed=embed)

    @commands.command()
    async def itemids(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        ITEMS = return_drops()

        id_string = ""
        id = 0
        for item in ITEMS:
            id_string += f"**{id}:** `{item['name']}`\n"
            id += 1

        await ctx.send(id_string)
        
    
class RewardSelection(menus.Menu):
    global reward_instance

    async def send_initial_message(self, ctx, channel):
        embed = discord.Embed(
            colour= discord.Colour.orange(),
            title = "Your rewards!"
        )

        rewards = reward_instance[self._author_id]['rewards']

        for item in rewards:
            stars = ""
            for i in range(item['rarity']):
                stars += "<:RRStar:825357537209090098> " 
            embed.add_field(name=item['name'], value=f"<:RRtoken:825288414789107762> `{item['tokens']}`\n{stars}", inline=True)

        #embed.add_field(name="DEBUG", value=reward_instance.keys())
        #embed.set_footer(text=f"Author id: {self._author_id}")

        box_img_url = "https://i.imgur.com/dSuvqsW.png"

        embed.set_thumbnail(url=box_img_url)
        embed = functions.embed_footer(ctx, embed)

        return await channel.send(embed=embed)

    async def update_menu(self, reward):
        global reward_instance
        global inventories
        item = reward_instance[self._author_id]['rewards'][reward]

        embed = discord.Embed(
            colour= discord.Colour.orange(),
            title = "Reward chosen!"
        )

        stars = ""
        for i in range(item['rarity']):
            stars += "<:RRStar:825357537209090098> " 

        embed.add_field(name=item['name'], value=f"<:RRtoken:825288414789107762> `{item['tokens']}`\n{stars}", inline=False)
        embed.set_thumbnail(url=item['img_url'])

        await self.message.edit(embed=embed)
        reward_instance.pop(self._author_id, None)
        if self._author_id not in inventories.keys():
            print("Inventory doesn't exist yet!")
            inventories[self._author_id] = {}

        author_inventory = inventories[self._author_id]
        if item['category'] == "tokens":
            print("TOKENS!")
            try:
                author_inventory['tokens'] += item['tokens']
            except:
                author_inventory['tokens'] = item['tokens']
        elif item['name'] not in author_inventory :
            print("Item not in inventory yet!")
            author_inventory[item['name']] = {'amount': 1}
        else:
            print("Item in inventory!")
            author_inventory[item['name']]['amount'] += 1

        print("SUCCESS")
        print(inventories)

        self.stop()

    async def reward_selection(amount=3):
        is_token_reward = False
        rewards = []
        for x in range(amount):
            item = None
            while not item: 
                item = random_drop()
                if item not in rewards: # Check for duplicate
                    # No duplicate tokens
                    if item['category'] == "tokens":
                        if is_token_reward:
                            item = None
                            continue
                        else:
                            is_token_reward = True
                    # Add reward to list
                    rewards.append(item)
                else: item = None
            #print(f"You got {item['name']}! It's worth {item['tokens']} tokens!")
        return rewards
        #print(rewards)

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
    client.add_cog(Economy(client))