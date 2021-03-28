import functions
import json
import discord
from discord.ext import commands
from discord.ext import menus
import random
import os

econ_path = "/home/runner/RecNetBotV2/Economy"
reward_instance = {}
default_player_data = {
    "level": 0,
    "level_next": 25, 
    "exp": 0, 
    "tokens": 0, 
    "boxes_opened": 0, 
    "badges": [],
    "inventory": []
}

def return_drops(category=None):
    global econ_path
    items = []
    try:
        if category:
            with open(f'{econ_path}/items/{category}.json') as json_file:
                items = json.load(json_file)
        else:   
            for file in os.listdir(f"{econ_path}/items/"):
                if file.endswith(".json"):
                    with open(f'{econ_path}/items/{file}') as json_file:
                        items += json.load(json_file)
    except:
        return None

    return items

async def get_items_of_rarity(rarity=1):
    ITEMS = return_drops()
    item_pool = []
    for item in ITEMS:
        if item['rarity'] == rarity:
            item_pool.append(item)
    return item_pool


async def random_drop():
    chance = random.randint(1, 200)
    print(str(chance) + "%")
    if chance > 80:
        # 1 Star
        item_pool = await get_items_of_rarity(1)
    elif chance > 60:
        # 2Star
        item_pool = await get_items_of_rarity(2)
    elif chance > 3:
        # 3 Star
        item_pool = await get_items_of_rarity(3)
    elif chance > 2:
        # 4 Star
        item_pool = await get_items_of_rarity(4)
    else:
        # 5 Star
        item_pool = await get_items_of_rarity(5)
    
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


#yeye, dupe
def save_player_data(data, user_id=None, reset=False):
    global econ_path
    if user_id:
        player_data = load_player_data(user_id)
        
        player_data[str(user_id)] = data

        data = player_data

    os.remove(f"{econ_path}/player_data.json") 
    with open(f"{econ_path}/player_data.json", 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4) 

def save_json(data, to_file):
    global econ_path

    os.remove(f"{econ_path}/{to_file}.json") 
    with open(f"{econ_path}/{to_file}.json", 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4) 

def load_json(file):
    with open(f'{econ_path}/{file}.json') as json_file:
        return json.load(json_file)

def reset_user_data(user_id):
    global default_player_data
    global econ_path
    player_data = load_json("player_data")
    
    player_data[str(user_id)] = default_player_data
    
    save_player_data(player_data)

    return player_data

def load_player_data(user_id=None):
    global econ_path
    global default_player_data
    player_data = load_json("player_data")

    if str(user_id) not in player_data.keys():
        print("User not in data list!")
        player_data = reset_user_data(user_id)

    # resave = False
    # for key in default_player_data:
    #     if not key in player_data[str(user_id)]:
    #         resave = True
    #         player_data[str(user_id)][key] = default_player_data[key]

    # if resave:
    #     print("RESAVE")
    #     save_json(player_data, "player_data")

    return player_data


async def add_to_inventory(user_id, id, amount):
    player_data = load_player_data(user_id)

    user_id, amount = int(user_id), int(amount)
    
    parsed_id = await parse_id(id)
    item = await get_item_data(parsed_id)
    item_id = await dump_id(parsed_id)

    if item['category'] == "tokens":
        print("TOKENS!")
        try:
            player_data[str(user_id)]['tokens'] += item['tokens']
        except:
            player_data[str(user_id)]['tokens'] = item['tokens']
    else:
        try:
            item_in_list = next(item for item in player_data[str(user_id)]['inventory'] if item["item"] == item_id)
            item_index = player_data[str(user_id)]['inventory'].index(item_in_list)
            player_data[str(user_id)]['inventory'][item_index]['amount'] += amount   
        except:
            print("Item not in inventory yet!")
            item_to_add = {"item": item_id, "amount": amount}
            player_data[str(user_id)]['inventory'].append(item_to_add)

    save_player_data(player_data)


async def remove_from_inventory(user_id, id, amount):
    player_data = load_player_data(user_id)

    user_id, amount = int(user_id), int(amount)
    
    id = await parse_id(id)
    item = await get_item_data(id)
    id = await dump_id(id)

    if item['category'] == "tokens":
        return

    if id not in player_data[str(user_id)]['inventory']:
        print("Item not in inventory yet!")
        return

    else:
        print("Item in inventory!")
        if amount > player_data[str(user_id)]['inventory'][id]['amount']:
            player_data[str(user_id)]['inventory'][id]['amount'] = 0
        else:
            player_data[str(user_id)]['inventory'][id]['amount'] -= amount

    save_player_data(player_data)


async def get_item_data(item_id):
    id = await parse_id(item_id)

    if not id:
        return None

    ITEMS = return_drops(id['category'])

    if not ITEMS:
        return None

    return ITEMS[id['index']]


async def dump_id(parsed_id):
    return f"{parsed_id['category']}:{parsed_id['index']}"


async def parse_id(id):
    if type(id) is dict:
        return id

    second_try = False
    while id:
        if ":" not in id:
            if second_try:
                return None
            id = await get_id(id)
            second_try = True
        split_id = id.split(":")
        parsed_id = {"category": split_id[0], "index": int(split_id[1])}
        return parsed_id
    return None


async def get_id(item_name):
    ITEMS = return_drops()

    old_category = ""
    for item in ITEMS:
        if old_category != item['category']:
            id = 0
            old_category = item['category']

        if item['name'].lower() == item_name.lower():
            return f"{item['category']}:{id}"

        id += 1


async def set_tokens(user_id, amount):
    player_data = load_player_data(user_id)
    user_id, amount = int(user_id), int(amount)

    player_data[str(user_id)]['tokens'] = amount
    save_player_data(player_data)


def add_xp(user_id, xp):
    player_data = load_player_data(user_id)

    player_data[str(user_id)]['exp'] += xp

    while player_data[str(user_id)]['exp'] >= player_data[str(user_id)]['level_next']:
        player_data[str(user_id)]['level'] += 1
        player_data[str(user_id)]['exp'] - player_data[str(user_id)]['level_next']
        player_data[str(user_id)]['level_next'] = round(player_data[str(user_id)]['level_next'] * 1.5)

    save_player_data(player_data)


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
    async def give(self, ctx, mention: discord.User, item_id, amount=1):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        try:
            await add_to_inventory(mention.id, item_id, amount)
            item_data = await get_item_data(item_id)
            await ctx.send(f"{amount}x `{item_data['name']}` given to {mention}!")
        except:
            await ctx.send(f"Couldn't give the item `{item_id}` to {mention}!")

    
    @commands.command()
    async def gift(self, ctx, mention: discord.User, item_name, amount=1):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        if not amount > 0:
            return await ctx.send("No stealing...")
        if mention.id == ctx.author.id:
            return await ctx.send("Gift to somebody else!")
        try:
            player_data = load_player_data(ctx.author.id)

            item_id = await get_id(item_name)
            item_data = await get_item_data(item_id)

            if amount > player_data[str(ctx.author.id)]['inventory'][item_id]['amount']:
                amount = player_data[str(ctx.author.id)]['inventory'][item_id]['amount']

            if amount == 0:
                return await ctx.send(f"You don't have any {item_data['emoji_icon']} `{item_name}`!")

            await remove_from_inventory(ctx.author.id, item_id, amount)
            item_data = await get_item_data(item_id)
            await add_to_inventory(mention.id, item_id, amount)
            await ctx.send(f"**{ctx.author}** gave **{mention}** {amount}x {item_data['emoji_icon']} `{item_data['name']}`!")
        except:
            await ctx.send(f"Couldn't give the item `{item_id}` to {mention}!")

    @gift.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Usage: `.gift <mention> \"item name\" <amount>`")
            
            await ctx.send(embed=embed)
        else:
            raise error

    
    @commands.command()
    @commands.check(functions.is_it_me)
    async def remove(self, ctx, mention: discord.User, item_id, amount=1):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        try:
            await remove_from_inventory(mention.id, item_id, amount)
            item_data = await get_item_data(item_id)
            await ctx.send(f"{amount}x `{item_data['name']}` taken away from {mention}!")
        except:
            await ctx.send(f"Couldn't take away the item `{item_id}` from {mention}!")

    
    @commands.command(aliases=["ii"])
    async def iteminfo(self, ctx, *item_name):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        item_name = " ".join(item_name[:])
        id = await get_id(item_name)
        item = await get_item_data(id)

        data_string = f"**Id**: {id}\n"
        for key in item:
            data_string += f"**{key}:** {item[key]}\n"

        return await ctx.send(data_string)

        await ctx.send(f"Item: `{item_name}`\nId: `{id}`")

    @commands.command()
    @commands.check(functions.is_it_me)
    async def settokens(self, ctx, mention: discord.User, amount):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        await set_tokens(mention.id, amount)

    
    @commands.command(aliases=['inv'])
    async def inventory(self, ctx, mention: discord.User = None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        if mention:
            player_data = load_player_data(mention.id)
        else:
            mention = ctx.author
            player_data = load_player_data(ctx.author.id)

        auth_inv = player_data[str(mention.id)]['inventory']

        inventory = []
        inventory_string = ""
        networth_tokens = 0
        for item in auth_inv:
            if item['amount'] < 1:
                continue
            item_data = await get_item_data(item['item'])
            item_data['amount'] = item['amount']

            inventory.append(item_data)

            #inventory_string += f"{item}: `{auth_inv[item]['amount']}`\n"
            item_worth = item_data['tokens'] * item['amount']
            networth_tokens += item_worth
        
        def sort_by_amount(list):
            return list['amount']

        inventory.sort(key=sort_by_amount, reverse=True)

        for item in inventory:
            if item['rarity'] == 5:
                inventory_string += f"{item['emoji_icon']} **{item['name']}**: `{item['amount']}`\n"
            else:
                inventory_string += f"{item['emoji_icon']} {item['name']}: `{item['amount']}`\n"

        embed = discord.Embed(
            colour= discord.Colour.orange(),
            title = f"{mention}'s Inventory",
            description = inventory_string
        )

        embed.add_field(name="Tokens", value=f"<:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens']}`", inline=False)
        embed.add_field(name="Item net worth", value=f"<:RRtoken:825288414789107762> `{networth_tokens}`", inline=False)

        embed.set_thumbnail(url=mention.avatar_url)
        embed = functions.embed_footer(ctx,embed)
        await ctx.send(embed=embed)

    @commands.command()
    async def itemids(self, ctx, item_id=None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        if item_id:
            item = await get_item_data(item_id)

            if not item:
                return await ctx.send(f"No item with the id `{item_id}`!")

            data_string = f"**Id**: {item_id}\n"
            for key in item:
                data_string += f"**{key}:** {item[key]}\n"

            return await ctx.send(data_string)

        ITEMS = return_drops()

        id_string = ""
        old_category = ""
        for item in ITEMS:
            #id_string += f"**{id}:** `{item['name']}`\n"
            if old_category != item['category']:
                id = 0
                old_category = item['category']

            id_string += f"`{item['category']}:{id}` ({item['name']})\n"
            id += 1

        await ctx.send(id_string)

    @commands.command(aliases=['ep'])
    async def econprofile(self, ctx, mention: discord.User = None):
        if mention:
            user = mention
        else:
            user = ctx.author
        player_data = load_player_data(user.id)

        embed = discord.Embed(
            colour= discord.Colour.orange(),
            title = f"{user}'s Economy Profile",
            description = f"Level: `{player_data[str(user.id)]['level']}`\nXP: `{player_data[str(user.id)]['exp']}`\nBoxes opened: `{player_data[str(user.id)]['boxes_opened']}`"
        )

        embed.add_field(name="Badges", value="None", inline=False)

        embed.set_thumbnail(url=user.avatar_url)
        embed = functions.embed_footer(ctx,embed)
        await ctx.send(embed=embed)
        

    
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
            embed.add_field(name=f"{item['emoji_icon']} {item['name']}", value=f"<:RRtoken:825288414789107762> `{item['tokens']}`\n{stars}", inline=True)

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

        embed.add_field(name=f"{item['emoji_icon']} {item['name']}", value=f"<:RRtoken:825288414789107762> `{item['tokens']}`\n{stars}", inline=False)
        embed.set_footer(text=f"Given to {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=item['img_url'])

        await self.message.edit(embed=embed)
        reward_instance.pop(self._author_id, None)

        await add_to_inventory(self._author_id, await get_id(item['name']), 1)

        player_data = load_player_data(self._author_id)
        player_data[str(ctx.author.id)]['boxes_opened'] += 1

        if item['rarity'] == 5:
            add_xp(self._author_id, 30)
        elif item['rarity'] == 4:
            add_xp(self._author_id, 20)
        elif item['rarity'] == 3:
            add_xp(self._author_id, 15)
        elif item['rarity'] == 2:
            add_xp(self._author_id, 10)
        else:
            add_xp(self._author_id, 5)

        save_player_data(player_data)

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