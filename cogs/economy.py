import functions
import json
import discord
from discord.ext import commands
from discord.ext import menus
import random
import os

econ_path = "/home/runner/RecNetBotV2/Economy"
reward_instance = {}

def return_drops(category=False):
    global econ_path
    items = []
    if category:
        with open(f'{econ_path}/items/{category}.json') as json_file:
            items = json.load(json_file)
    else:   
        for file in os.listdir(f"{econ_path}/items/"):
            if file.endswith(".json"):
                with open(f'{econ_path}/items/{file}') as json_file:
                    items += json.load(json_file)

    return items


async def random_drop():
    chance = random.randint(1, 200)
    print(str(chance) + "%")
    if chance > 120:
        # Film
        item_pool = return_drops("film")
    elif chance > 60:
        # Pizza / Donuts / Pretzels / Root Beer
        item_pool = return_drops("pizza") + return_drops("donuts") + [return_drops("other")[0]] + [return_drops("drinks")[0]]
    elif chance > 20:
        # Popcorn / KO
        item_pool = return_drops("ko") + [return_drops("other")[1]]
    elif chance > 10:
        # 10 / 25 Tokens
        item_pool = [return_drops("tokens")[0]] + [return_drops("tokens")[1]]
    elif chance > 3:
        # 50 Tokens / Cake
        item_pool = [return_drops("tokens")[2]] + return_drops('cake')
    elif chance > 1:
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
            item = await random_drop()
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

async def save_inv(inventories):
    global econ_path
    os.remove(f"{econ_path}/inventories.json") 
    with open(f"{econ_path}/inventories.json", 'w') as file:
        json.dump(inventories, file, ensure_ascii=False, indent=4)    

async def load_inv(user_id=None, return_user_inv=False):
    global econ_path
    with open(f'{econ_path}/inventories.json') as file:
        inventories = json.load(file)

    if user_id and str(user_id) not in inventories.keys():
        print("User not in inventory list!")
        inventories[str(user_id)] = {}
    
    if return_user_inv and user_id:
        return inventories[str(user_id)]
    return inventories


async def add_to_inventory(user_id, item_index, amount):
    inventories = await load_inv(user_id)

    user_id, amount = int(user_id), int(amount)
    try:
        item_index = int(item_index)
    except:
        item_index = str(item_index)

    print(type(item_index))
    
    if type(item_index) is int:
        item = await get_item_data(item_index, True)
        #item = ITEMS[int(item_index)]
    else:
        item = await get_item_data(item_index, False)

    if item['category'] == "tokens":
        print("TOKENS!")
        try:
            inventories[str(user_id)]['tokens'] += item['tokens']
        except:
            inventories[str(user_id)]['tokens'] = item['tokens']
    elif item['name'] not in inventories[str(user_id)]:
        print("Item not in inventory yet!")
        inventories[str(user_id)][item['name']] = {'amount': amount}
    else:
        print("Item in inventory!")
        inventories[str(user_id)][item['name']]['amount'] += amount

    await save_inv(inventories)

async def get_item_data(item, index=False):
    ITEMS = return_drops()
    if index:
        return ITEMS[index]
    else:
        for item_ in ITEMS:
            if item_['name'] == item:
                return item_


async def set_tokens(user_id, amount):
    inventories = await load_inv(user_id)
    user_id, amount = int(user_id), int(amount)

    inventories[str(user_id)]['tokens'] = amount
    await save_inv(inventories)


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
    async def inventory(self, ctx, mention: discord.User = None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        if mention:
            auth_inv = await load_inv(mention.id, True)
        else:
            mention = ctx.author
            auth_inv = await load_inv(ctx.author.id, True)

        inventory = []
        inventory_string = ""
        networth_tokens = 0
        for item in auth_inv:
            if item == "tokens":
                continue
            item_data = await get_item_data(item)

            inventory.append({"name": item, "rarity": item_data['rarity'], "amount": auth_inv[item]['amount']})

            #inventory_string += f"{item}: `{auth_inv[item]['amount']}`\n"
            item_worth = item_data['tokens'] * auth_inv[item]['amount']
            networth_tokens += item_worth
        
        def sort_by_amount(list):
            return list['amount']

        inventory.sort(key=sort_by_amount, reverse=True)

        for item in inventory:
            if item['rarity'] == 5:
                inventory_string += f"**{item['name']}**: `{item['amount']}`\n"
            else:
                inventory_string += f"{item['name']}: `{item['amount']}`\n"

        embed = discord.Embed(
            colour= discord.Colour.orange(),
            title = f"{mention}'s Inventory",
            description = inventory_string
        )

        if not "tokens" in auth_inv.keys():
            auth_inv['tokens'] = 0
        embed.add_field(name="Tokens", value=f"<:RRtoken:825288414789107762> `{auth_inv['tokens']}`", inline=False)
        embed.add_field(name="Item net worth", value=f"<:RRtoken:825288414789107762> `{networth_tokens}`", inline=False)

        print(auth_inv)
        embed.set_thumbnail(url=mention.avatar_url)
        embed = functions.embed_footer(ctx,embed)
        await ctx.send(embed=embed)

    @commands.command()
    async def itemids(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        ITEMS = await return_drops()

        id_string = ""
        id = 0
        for item in ITEMS:
            id_string += f"**{id}:** `{item['name']}`\n"
            id += 1

        await ctx.send(id_string)
        
    
class RewardSelection(menus.Menu):
    global reward_instance

    async def send_initial_message(self, ctx, channel):
        reward_instance[self._author_id]['ctx'] = ctx

        embed = discord.Embed(
            colour = 0x2f3136,
            title = "Choose a reward!"
        )

        rewards = reward_instance[self._author_id]['rewards']

        for item in rewards:
            stars = ""
            if item['category'] != "tokens":
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
        item = reward_instance[self._author_id]['rewards'][reward]
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
            title = "Reward chosen!"
        )

        stars = ""
        if item['category'] != "tokens":
            for i in range(item['rarity']):
                stars += "<:RRStar:825357537209090098> " 

        embed.add_field(name=item['name'], value=f"<:RRtoken:825288414789107762> `{item['tokens']}`\n{stars}", inline=False)
        embed.set_footer(text=f"Given to {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=item['img_url'])

        await self.message.edit(embed=embed)
        reward_instance.pop(self._author_id, None)

        await add_to_inventory(self._author_id, item['name'], 1)

        self.stop()

    async def reward_selection(amount=3):
        is_token_reward = False
        rewards = []
        for x in range(amount):
            item = None
            while not item: 
                item = await random_drop()
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