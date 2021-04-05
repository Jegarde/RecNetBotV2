import json
import discord
import functions
from discord.ext import commands
from discord.ext import menus
import random
import os
import datetime
from datetime import date, datetime

econ_path = "/home/runner/RecNetBotV2/Economy"
buy_tax = 1
sell_tax = 0.8
reward_instance = {}
default_player_data = {
    "bio": "",
    "level": 0,
    "level_next": 10, 
    "exp": 0, 
    "luck": 0,
    "tokens": 1000, 
    "boxes_opened": 0, 
    "last_box": "",
    "last_daily_date": "",
    "last_daily_time": "",
    "daily_challenges": [0,0,0],
    "ko_boost": 0,
    "ko_boost_capacity": 1000,
    "badges": [],
    "stats": {
        "paintball":
        {
            "games_played": 0,
            "wins": 0,
            "ties": 0,
            "defeats": 0,
            "tags": 0,
            "outs": 0,
            "flags": 0,
            "exp_gained": 0
        }
    },
    "inventory": ["boxes:0","boxes:0","boxes:0","boxes:0","boxes:0"],
    "equipped": {"face": None, "hat": None, "shirt": None, "gloves": None, "back": None, "torso": None, "belt": None},
    "cosmetics": []
}

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

    print(f"Returned drops! Category: {category}")
    return items


async def parse_id(item_id):
    parsed_id = item_id.split(":")
    return {"category": parsed_id[0], "index": int(parsed_id[1])}


async def get_id(item_name):
    item_name = await check_ko_name(item_name)
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

async def give_badge(user_id, badge_index):
    player_data = await load_player_data()

    if badge_index not in player_data[str(user_id)]['badges']:
        badges = await load_badges()
        try:
            print(f"Badge {badge_index} found: {badges['badges'][badge_index]}")
        except:
            print(f"Badge {badge_index} not found!")
            return False

        player_data[str(user_id)]['badges'].append(int(badge_index))
        await save_player_data(player_data)


async def load_json(json_f):
    with open(f"{econ_path}/{json_f}.json", 'r') as f:
        json_file = json.load(f)

    return json_file


async def load_challenges():
    with open(f"{econ_path}/challenges.json", 'r') as f:
        json_file = json.load(f)

    return json_file


async def load_badges():
    global econ_path

    with open(f"{econ_path}/badges.json", 'r') as f:
        json_file = json.load(f)
    return json_file


async def get_badge_data(index):
    badges = await load_badges()

    return badges['badges'][index]


async def get_item_data(item_id):
    parsed_id = await parse_id(item_id)

    print(parsed_id)
    
    ITEMS = await return_drops(parsed_id['category'])

    return ITEMS[parsed_id['index']]


async def get_items_of_rarity(rarity=1):
    ITEMS = await return_drops()
    item_pool = []
    for item in ITEMS:
        if item['rarity'] == rarity:
            item_pool.append(item)
    print(f"Returned items of rarity {rarity}, count {len(item_pool)}")
    return item_pool


async def get_items_of_rarity_inv(user_id, rarity=1):
    ITEMS = await load_inventory(user_id)
    rar_items = []
    for item in ITEMS:
        if item['item']['rarity'] == rarity:
            rar_items.append(item)
    print(f"Returned items of rarity {rarity}, count {len(rar_items)}")
    return rar_items


async def ko_multiplier(user_id):
    player_data = await load_player_data()
    if player_data[str(user_id)]['ko_boost']:
        return round(1 + player_data[str(user_id)]['ko_boost'] * 0.0005, 3)
    else:
        return 1.0


async def random_drop(categories=[]):
    chance = random.randint(1, 300)
    if not categories:
        if chance < 200:
            # 1 Star
            item_pool = await get_items_of_rarity(1)
        elif chance < 80:
            # 2Star
            item_pool = await get_items_of_rarity(2)
        elif chance < 30:
            # 3 Star
            item_pool = await get_items_of_rarity(3)
        elif chance < 2:
            # 4 Star
            item_pool = await get_items_of_rarity(4)
        else:
            # 5 Star
            item_pool = await get_items_of_rarity(5)
    else:
        item_pool = []
        for category in categories:
            item_pool += await return_drops(category)
    
    item = random.choice(item_pool)
    print(f"Random drop - {item['name']} - {chance}% - rarity {item['rarity']}")
    return item
   

async def reward_selection(amount=3, categories=[], dupes=False):
    is_token_reward = False
    rewards = []
    for x in range(amount):
        item = None
        while not item: 
            item = await random_drop(categories)
            if (await get_id(item['name']) not in rewards) or dupes: # Check for duplicate
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


async def save_player_data(data):
    global econ_path

    with open(f"{econ_path}/player_data.json", 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4) 


async def update_player_data(user_id, key, value, set=True):
    player_data = await load_player_data()

    if type(value) is list:
        player_data[str(user_id)][str(key)] = value
        return await save_player_data(player_data)

    try:
        value = int(value)
        if set:
            player_data[str(user_id)][str(key)] = value
        else:
            player_data[str(user_id)][str(key)] += value
    except:
        value = str(value)
        player_data[str(user_id)][str(key)] = value

    await save_player_data(player_data)


async def update_inventory(user_id, item_id, amount=1, add=True):
    player_data = await load_player_data()

    item_data = await get_item_data(item_id)
    if item_data['category'] == "tokens":
        await update_player_data(user_id, "tokens", item_data['tokens'], False)
    elif item_data['wearable']:
        player_data[str(user_id)]['cosmetics'].append(item_id)
        await save_player_data(player_data)
    else:
        for i in range(amount):
            if add:
                if item_data['category'] == "boxes":
                    player_data[str(user_id)]['last_box'] = item_id
                player_data[str(user_id)]['inventory'].append(item_id)
            else:
                try:
                    player_data[str(user_id)]['inventory'].remove(item_id)
                except:
                    break

        await save_player_data(player_data)
        if item_id == "drinks:1":
            await give_badge(user_id, 2)


async def load_inventory(user_id):
    player_data = await load_player_data()

    inv = player_data[str(user_id)]['inventory']
    loaded_inv, temp_inv = [], []
    for item in inv:
        if item in temp_inv: # avoid dupes
            continue

        item_data = await get_item_data(item)
        inv_item_data = {"item": item_data, "amount": inv.count(item)}
        loaded_inv.append(inv_item_data)
        temp_inv.append(item)

    return loaded_inv


async def load_boxes(user_id):
    inv = await load_inventory(user_id)

    boxes = []
    for item in inv:
        if item['item']['category'] == "boxes": # check if it's a box
            boxes.append(item)
    
    return boxes


async def load_cosmetics(user_id):
    inv = await load_inventory(user_id)

    cosmetics = []
    for item in inv:
        if item['item']['wearable']:
            cosmetics.append(item)
    
    return cosmetics


async def item_count_in_inventory(user_id, item_id):
    player_data = await load_player_data()
    return player_data[str(user_id)]['inventory'].count(item_id)


async def load_player_data():
    global econ_path

    with open(f"{econ_path}/player_data.json", 'r') as f:
        json_file = json.load(f)
    return json_file
    

async def initialize_user(user_id, ctx=None):
    global econ_path
    global default_player_data
    player_data = await load_player_data()
    
    if str(user_id) in player_data:
        for key in default_player_data:
            if key not in player_data[str(user_id)].keys():
                player_data[str(user_id)][key] = default_player_data[key]
    else:
        player_data[str(user_id)] = default_player_data
    
    # Level up CHECK
    if ctx:
        if player_data[str(user_id)]['exp'] >= player_data[str(user_id)]['level_next']:
            rewards = []
            activity_unlock = ""
            token_reward = 0
            while player_data[str(user_id)]['exp'] >= player_data[str(user_id)]['level_next']:
                player_data[str(user_id)]['level'] += 1
                player_data[str(user_id)]['exp'] -= player_data[str(user_id)]['level_next']
                player_data[str(user_id)]['level_next'] = round(player_data[str(user_id)]['level_next'] * 1.5)

                for x in range(int(player_data[str(user_id)]['level'] / 10)):
                    rewards.append("drinks:1")

                if player_data[str(user_id)]['level'] == 10:
                    player_data[str(user_id)]['badges'].append(0)
                    activity_unlock = "\nUnlocked Paintball! `.play pb`\nReceived Early Supporter badge!"

                rewards.append("boxes:0")
                for i in range(int(player_data[str(user_id)]['level'] / 3)):
                    for i in range(int(player_data[str(user_id)]['level'] * 0.3)):
                        rewards.append("boxes:0")
                token_reward += 100 * player_data[str(user_id)]['level']

            claimed_rewards = []
            reward_string = f"<:RRtoken:825288414789107762> `{token_reward}`"
            for reward in rewards:
                player_data[str(user_id)]['inventory'].append(reward)
                
                item_data = await get_item_data(reward)
                item_name = item_data['name']
                if reward not in claimed_rewards:
                    reward_string += f"\n{rewards.count(reward)}x {item_data['emoji_icon']} {item_name}"
                
                claimed_rewards.append(reward)
            
            reward_string += activity_unlock

            player_data[str(user_id)]['tokens'] += token_reward

            embed = discord.Embed(
                title="Level up!",
                description=f"<@{user_id}> is now level **{player_data[str(user_id)]['level']}**!",
                colour=discord.Colour.green()
            )
            embed.add_field(name="Rewards", value=reward_string, inline=False)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed = functions.embed_footer(ctx, embed)

            await ctx.send(f"<@{user_id}>", embed=embed)

    await save_player_data(player_data)

    return


async def cosmetic_multiplier(user_id, activity):
    player_data = await load_player_data()

    multiplier = 1
    for key in player_data[str(user_id)]['equipped']:
        item_id = player_data[str(user_id)]['equipped'][key]
        if not item_id:
            continue
        item_data = await get_item_data(player_data[str(user_id)]['equipped'][key])

        if item_data['activity'].lower() == activity.lower():
            multiplier += item_data['multiplier']

    return multiplier


async def load_activity_dialogue(activity, type_):
    global econ_path

    with open(f'{econ_path}/activities/{activity}.json') as json_file:
        dialogue = json.load(json_file)

    return dialogue['dialogue'][type_]


async def update_stats(user_id, activity, key, value, set_=False):
    player_data = await load_player_data()

    if set_:
        player_data[str(user_id)]['stats'][activity][key] = value
    else:
        player_data[str(user_id)]['stats'][activity][key] += value

    await save_player_data(player_data)


async def load_stats(user_id, activity=None):
    player_data = await load_player_data()

    if activity:
        try:
            return player_data[str(user_id)]['stats'][activity]
        except:
            return False
    else:
        return player_data[str(user_id)]['stats']


async def probably(chance):
    return random.random() < chance


async def is_usable(item_id):
    try:
        item_data = await get_item_data(item_id)
        return item_data['usable']
    except:
        return False

    return False


async def check_ko_name(item_name):
    ko_drops = await return_drops("ko")
    for item in ko_drops:
        ko_name = item['name'].split(item['name'][:10])[1]
        if ko_name.lower() == item_name.lower():
            item_name = item['name']

    return item_name


class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client

    #CMD-GUIDE
    @commands.command()
    async def guide(self, ctx):
        embed = discord.Embed(
            title="RNB Economy Guide!",
            description="All the basics you need to know to get started!\n*`.help economy` for more help!*",
            colour = discord.Colour.orange()
        )

        embed.add_field(name="<a:spinning:804022054822346823> Basics", value="Use `.econprofile` to check your Economy profile! You can look at your inventory with `.inventory`! Use `.sell <amount> <item>` to sell your items. Selling items gives you tokens, that you can spend to buy more items or boxes! There is a 20% tax when selling items. Use `.buy <amount> <item>` to buy new items. Consuming items give you XP boosts, EXP or boosts luck. Use `.use <item>` to do so.",inline=False)

        embed.add_field(name="<:RNBBox:826478764141576192> Boxes", value="You receive boxes from daily challenges, (`.daily`) activities (`.play`), by buying them (`.boxes`) or sometimes from boxes themselves. Boxes gives you 3 random reward choices, just like in Rec Room. You can open a box by doing `.unbox <box>`. If you don't have the box you're trying to unbox, it'll prompt you to buy one. If you open a box, you can just do `.unbox` again to open another one of the previous box.",inline=False)

        embed.add_field(name="<:KOTire:825646277983076393> Activities", value="You can play activities to get rewards! Use `.play` to see all the activities. They are currently in a very early stage, and will be updated to be more involved in the future. You can receive boxes, activity specific consumables, costumes or a rare Bubbly! To see your equipped outfits, do `.mirror`.",inline=False)

        embed.add_field(name="<:RRtoken:825288414789107762> Making tokens", value="A great way to make tokens is just opening boxes. Boxes usually profit, and if not, you will receive EXP anyways. Level up rewards get you boxes and tokens. Cake boxes are a great way to get EXP, because every cake is 4 star. The better the rarity, the more EXP you gain. If you somehow lost all your tokens, you can always `.beg`. Film boxes are a decent way to get a little token when you're absolutely broke, because you always profit from them. (a whopping 4 tokens!) If you're above level 10, just playing Paintball is a fantastic way to make tokens.",inline=False)

        embed.set_thumbnail(url="https://i.imgur.com/Fyb9qXz.png")
        embed = functions.embed_footer(ctx, embed)
        await ctx.send(embed=embed)


    #CMD-RBOX
    @commands.command()
    async def rbox(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        await initialize_user(ctx.author.id, ctx)

        user_boxes = await load_boxes(ctx.author.id)

        if user_boxes:
            box = random.choice(user_boxes)['item']
            box_id = await get_id(box['name'])
            box_data = await get_item_data(box_id)

            await update_inventory(ctx.author.id, box_id, 1, False)

            global reward_instance # I hate doing this, but it works.
            reward_instance[ctx.author.id] = {"rewards": await reward_selection(3, box_data['drops'], box_data['dupes']), "box_data": box_data}
            menu = RewardSelection()
            await menu.start(ctx)

        else:
            await ctx.send("You don't have any boxes!\n`.boxes`")


    #CMD-ITEM
    @commands.command()
    async def item(self, ctx, *item_name):
        item_name = str(" ".join(item_name[:]))
        item_id = await get_id(item_name)

        if item_id:
            item_data = await get_item_data(item_id)

            item_desc = ""
            try:
                item_desc = item_data['desc']
            except:
                item_desc = "None!"

            if item_data['rarity'] == 5:
                color = discord.Colour.orange()
            elif item_data['rarity'] == 4:
                color = discord.Colour.purple()
            elif item_data['rarity'] == 3:
                color = discord.Colour.blue()
            elif item_data['rarity'] == 2:
                color = discord.Colour.green()
            else:
                color = discord.Colour.dark_gray()

            embed = discord.Embed(
                title=f"{item_data['emoji_icon']} {item_data['name']}",
                description=f"**Description:** {item_desc}",
                colour=color
            )

            for key in item_data:
                embed.add_field(name=key, value=item_data[key], inline=False)

            embed.set_image(url=item_data['img_url'])
            embed = functions.embed_footer(ctx,embed)
            await ctx.send(embed=embed)
        else:
            if item_name:
                await ctx.send(f"`{item_name}` doesn't exist!")
            else:
                await ctx.send("Include in an item!\n**Usage:** `.item <item>`")


    #CMD-EXCHANGE
    @commands.command()
    async def exchange(self, ctx, *item):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        await initialize_user(ctx.author.id, ctx)

        pass


    #CMD-PLAY
    @commands.command()
    @commands.cooldown(12, 65, commands.BucketType.user)
    async def play(self, ctx, *activity):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        await initialize_user(ctx.author.id, ctx)

        player_data = await load_player_data()

        activity = " ".join(activity[:])
        activities = ["paintball", "pb", "park", "golden trophy"]

        if activity.lower() not in activities:
            embed = discord.Embed(
                title="Activity list",
                description="`.play <activity>`",
                colour=discord.Colour.orange()
            )

            locked_str = ""
            if player_data[str(ctx.author.id)]['level'] < 10:
                locked_str = "**Unlocked at level `10`!**\n"
            embed.add_field(name="Paintball", value=f"{locked_str}Red and Blue teams splat each other in capture the flag and team battle.", inline=False)
            embed.add_field(name="Golden Trophy [NOT YET READY]", value="The goblin king stole Coach's Golden Trophy. Team up and embark on an epic quest to recover it!", inline=False)
            embed.add_field(name="Park [NOT YET READY]", value="A sprawling park with amphitheater, play fields, and a cave.", inline=False)

            return await ctx.send(embed=embed)
    

        if activity.lower() in ("paintball", "pb"):
            if player_data[str(ctx.author.id)]['level'] < 10:
                return await ctx.send("You're not experienced enough! Come back when you're at least level `10`!")

            kills = random.randint(0, 20+player_data[str(ctx.author.id)]['level'])
            deaths = random.randint(0, 35)
            flags = random.randint(0, 3)

            result = {"victory": False, "type": 1} 

            kill_ratio = kills - deaths
            if kills < 0:
                kills = 0

            if flags == 3:
                # CTF Win
                result = {"victory": True, "type": 0} 
            elif await probably(40 / 100):
                # CTF Defeat
                result = {"victory": False, "type": 2} 
            elif flags == 0:
                # TDM
                victory_chance = random.randint(kill_ratio, 70)
                if victory_chance > kills:
                    # TDM Win
                    result = {"victory": True, "type": 0} 
                else:
                    # TDM Defeat
                    result = {"victory": False, "type": 2} 
            else:
                # Hmm....
                result = {"victory": False, "type": 1} 

            rewards =  {"exp": 0, "rewards": []}
            boxes = await return_drops("boxes")
            if result['type'] == 0: 
                await update_stats(ctx.author.id, "paintball", "wins", 1, False) # Update stats
                color = discord.Colour.green()

                victory = "Victory!"
                rewards['exp'] += 35
                if await probably(50 / 100): 
                    box_id = await get_id(random.choice(boxes)['name'])
                    if not box_id == "boxes:6":
                        rewards['rewards'].append(box_id)

                if await probably(1 / 500): 
                    rewards['rewards'].append("boxes:6")

                # Rare bubbly drop
                if await probably(1 / 200):
                    rewards['rewards'].append("drinks:1")

            elif result['type'] == 1:
                await update_stats(ctx.author.id, "paintball", "ties", 1, False) # Update stats
                color = discord.Colour.gold()

                victory = "Tie!"
                rewards['exp'] += 10
                if await probably(15 / 100):
                    box_id = await get_id(random.choice(boxes)['name'])
                    if not box_id == "boxes:6":
                        rewards['rewards'].append(box_id)

                if await probably(1 / 600): 
                    rewards['rewards'].append("boxes:6")
            else:
                await update_stats(ctx.author.id, "paintball", "defeats", 1, False) # Update stats
                color = discord.Colour.red()

                victory = "Defeat!"
                rewards['exp'] += 5
                if await probably(5 / 100):     
                    box_id = await get_id(random.choice(boxes)['name'])
                    if not box_id == "boxes:6":
                        rewards['rewards'].append(box_id)

                if await probably(1 / 700): 
                    rewards['rewards'].append("boxes:6")

            # Passive drops
            if await probably(30 / 100):
                ko = await return_drops("ko")
                item_id = await get_id(random.choice(ko)['name'])
                rewards['rewards'].append(item_id)

            boost_exp = int((kills * 1.2) * await ko_multiplier(ctx.author.id))
            rewards['exp'] += int((flags * 3) + boost_exp + (deaths * 0.7)+(player_data[str(ctx.author.id)]['level']*1.5))

            dialogue = await load_activity_dialogue("paintball", result['type'])
            dialogue = random.choice(dialogue)

            print(dialogue)
            
            result_string = ""
            if "{user}" in dialogue:
                result_string = dialogue.format(user=ctx.author)
    
            embed = discord.Embed(
                title="Paintball results",
                colour=color
            )

            boost_string = ""
            if player_data[str(ctx.author.id)]['ko_boost'] > 0:
                if player_data[str(ctx.author.id)]['ko_boost'] - kills < 0:
                    await update_player_data(ctx.author.id, "ko_boost", 0, True)
                else:
                    await update_player_data(ctx.author.id, "ko_boost", -kills, False)
                boost_string = f" (+{boost_exp} EXP)"

            embed.add_field(name=victory, value=result_string, inline=False)
            embed.add_field(name="Results", value=f"Tags: `{kills}`{boost_string}\nOuts: `{deaths}`\nFlags: `{flags}`", inline=False)

            reward_string = ""
            for reward in rewards['rewards']:
                await update_inventory(ctx.author.id, reward, 1, True)
                item_data = await get_item_data(reward)
                reward_string += f"{item_data['emoji_icon']} {item_data['name']} "
            if not reward_string:
                reward_string = "None!"

            gb_string = ""
            extra_xp = 0
            gear_boost = await cosmetic_multiplier(ctx.author.id, "paintball")
            if not gear_boost == 1:
                extra_xp = gear_boost * rewards['exp'] - rewards['exp']
                gb_string = f"(+{extra_xp} EXP)"

            embed.add_field(name="Rewards", value=f"Exp gained: `{rewards['exp']}` {gb_string}\nRewards: {reward_string}", inline=False)
            rewards['exp'] += extra_xp # costume multiplier
            # Give rewards / update stats
            await update_player_data(ctx.author.id, "exp", rewards['exp'], False)
            await update_stats(ctx.author.id, "paintball", "exp_gained", rewards['exp'], False)
            await update_stats(ctx.author.id, "paintball", "tags", kills, False)
            await update_stats(ctx.author.id, "paintball", "outs", deaths, False)
            await update_stats(ctx.author.id, "paintball", "flags", flags, False)
            await update_stats(ctx.author.id, "paintball", "games_played", 1, False)
            

        embed.set_thumbnail(url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @play.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="Time to take a break, buddy.",
                description=f"Try again in {int(error.retry_after)} seconds.", 
                color=discord.Colour.red()
            )
            embed = functions.embed_footer(ctx, embed)
            await ctx.send(embed=embed)


    #CMD-MIRROR
    @commands.command(aliases=['equipment'])
    async def mirror(self, ctx, mention: discord.User=None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        if mention:
            user = mention
        else:
            user = ctx.author

        await initialize_user(user.id)
        player_data = await load_player_data()

        embed = discord.Embed(
            title=f"{user}'s Equipment",
            description="`.equip <cosmetic>`\n`.unequip <cosmetic|all>`",
            colour=discord.Colour.orange()
        )
        #{"face": None, "hat": None, "shirt": None, "lhand": None, "rhand": None, "back": None, "torso": None, "belt": None}

        for key in player_data[str(user.id)]['equipped']:
            if player_data[str(user.id)]['equipped'][key]:
                item_data = await get_item_data(player_data[str(user.id)]['equipped'][key])
                item_desc = f"{item_data['emoji_icon']} {item_data['name']}\nx{item_data['multiplier']} EXP in {str(item_data['activity'].capitalize())}"
            else:
                item_desc = "None!"
                
            embed.add_field(name=key.capitalize(), value=item_desc, inline=False)

        embed.add_field(name="Paintball multiplier", value=f"x{await cosmetic_multiplier(user.id, 'paintball')}", inline=False)
        embed.add_field(name="Box EXP multiplier", value=f"x{await cosmetic_multiplier(user.id, 'box')}", inline=False)

        embed.set_thumbnail(url=user.avatar_url)
        embed = functions.embed_footer(ctx,embed)
        await ctx.send(embed=embed)


    #CMD-EQUIP
    @commands.command()
    async def equip(self, ctx, *item_name):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        await initialize_user(ctx.author.id)
        player_data = await load_player_data()

        item_name = str(" ".join(item_name[:]))

        if item_name:
            item_id = await get_id(item_name)
            if item_id:
                item_data = await get_item_data(item_id)

                if item_data['wearable']:
                    if player_data[str(ctx.author.id)]['level'] < item_data['lvl']:
                        return await ctx.send(f"You can't equip {item_data['emoji_icon']} {item_data['name']}!\nYou need to be level {item_data['lvl']}!")

                    if item_id in player_data[str(ctx.author.id)]['cosmetics']:
                        player_data[str(ctx.author.id)]['equipped'][item_data['slot']] = item_id
                        await save_player_data(player_data)

                        await ctx.send(f"Equipped {item_data['emoji_icon']} {item_data['name']} in {item_data['slot']} slot!\n`.mirror`")
                    else:
                        await ctx.send(f"You don't have {item_data['emoji_icon']} {item_data['name']}!")
                else:
                    await ctx.send(f"You can't equip {item_data['emoji_icon']} {item_data['name']}!")
            else:
                await ctx.send(f"{item_name} doesn't exist!")
        else:
            await ctx.send("Include in a cosmetic!\n**Usage:** `.equip <cosmetic>`")

    
    #CMD-UNEQUIP
    @commands.command()
    async def unequip(self, ctx, slot=None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        await initialize_user(ctx.author.id)
        player_data = await load_player_data()

        slot = slot.lower()

        if slot:
            if slot.lower() == "all":
                player_data[str(ctx.author.id)]['equipped'] = {"face": None, "hat": None, "shirt": None, "gloves": None, "back": None, "torso": None, "belt": None}
                await save_player_data(player_data)
                return await ctx.send("Unequipped all items!\n`.mirror`")
            try:
                if player_data[str(ctx.author.id)]['equipped'][slot]:
                    item_data = await get_item_data(player_data[str(ctx.author.id)]['equipped'][slot])
                    player_data[str(ctx.author.id)]['equipped'][slot] = None
                    await save_player_data(player_data)
                else:
                    return await ctx.send(f"You don't have anything equipped in {slot} slot!\n`.mirror`")
            except:
                return await ctx.send(f"\"{slot}\" slot doesn't exist!\n`.mirror`")
            
            await ctx.send(f"Unequipped {item_data['emoji_icon']} {item_data['name']} in {item_data['slot']} slot!\n`.mirror`")
        else:
            await ctx.send("Include in a slot!\n**Usage:** `.unequip <slot>`")


    #CMD-INVENTORY
    @commands.command(aliases=['inv'])
    async def inventory(self, ctx, mention: discord.User = None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        if mention:
            user = mention
        else:
            user = ctx.author

        await initialize_user(user.id)
        player_data = await load_player_data()

        embed = discord.Embed(
            title=f"{user}'s Inventory",
            description="*Number next to rarity is the category's worth*",
            colour=discord.Colour.orange()
        )

        networth = 0
        inv = await load_inventory(user.id)

        def sort_by_amount(list):
            return list['amount']

        def sort_by_rarity(list):
            return list['item']['rarity']

        inv.sort(key=sort_by_rarity, reverse=True)

        inventory_string = "None!"
        box_string = "None! `.boxes`"
        cosmetic_string = "None! `.mirror`"

        if inv:
            try:
                temp_rarity = inv[0]['item']['rarity'] # get rarity of first item
            except:
                temp_rarity = 5

            inventory_string = ""
            rarity_worth = 0
            for item in inv:
                if item['item']['category'] == "boxes": # if it's a box, don't display among other items
                    continue

                #Rarity sorting
                if temp_rarity != item['item']['rarity']:
                    if inventory_string:
                        embed.add_field(name=f"{temp_rarity} Stars ({rarity_worth})", value=inventory_string, inline=False)
                    while temp_rarity != item['item']['rarity']:
                        temp_rarity -= 1
                    inventory_string = ""
                    rarity_worth = 0

                # Add item into inv sting
                inventory_string += f"{item['amount']}x {item['item']['emoji_icon']} {item['item']['name']}\n"
                rarity_worth += item['item']['tokens'] * item['amount']

                # Sum net worth while you're at it
                networth += item['item']['tokens'] * item['amount']

            if inventory_string: # After all items have been gone through, check if any left
                embed.add_field(name=f"{temp_rarity} Stars ({rarity_worth})", value=inventory_string, inline=False)
                inventory_string = ""
                rarity_worth = 0

            cosmetic_string = "None! `.mirror`"
            cosmetics = player_data[str(user.id)]['cosmetics']
            if cosmetics: # if there are any boxes
                cosmetic_string = ""
                temp_cosm = []
                for cosmetic in cosmetics:
                    if cosmetic in temp_cosm:
                        continue
                    cosmetic_data = await get_item_data(cosmetic)
                    cosmetic_string += f"{cosmetics.count(cosmetic)}x {cosmetic_data['emoji_icon']} {cosmetic_data['name']}\n"
                    temp_cosm.append(cosmetic)

            box_string = "None! `.boxes`"
            boxes = await load_boxes(user.id)
            if boxes: # if there are any boxes
                box_string = ""
                for box in boxes:
                    box_string += f"{box['amount']}x {box['item']['emoji_icon']} {box['item']['name']}\n"
        else:
            inventory_string = "None!"
            box_string = "None! `.boxes`"
            cosmetic_string = "None! `.mirror`"


        embed.add_field(name="Cosmetics", value=cosmetic_string , inline=False)
        embed.add_field(name="Boxes", value=box_string, inline=False)
        embed.add_field(name="Tokens", value=f"<:RRtoken:825288414789107762> `{player_data[str(user.id)]['tokens']}`", inline=False)
        embed.add_field(name="Item Net Worth", value=f"<:RRtoken:825288414789107762> `{networth}`", inline=True)
        embed.add_field(name="Total Net Worth", value=f"<:RRtoken:825288414789107762> `{networth+player_data[str(user.id)]['tokens']}`", inline=True)
        embed.set_thumbnail(url=user.avatar_url)
        embed = functions.embed_footer(ctx, embed)

        await ctx.send(embed=embed)

    @inventory.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.UserNotFound):
            await ctx.send("User not found!")
        else:
            raise error


    #CMD-BADGES
    @commands.command()
    async def badges(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        badges = await load_badges()

        embed = discord.Embed(
            title="Badges",
            colour=discord.Colour.orange(),
            description="All badges and their descriptions.\nRed ones are exclusive!"
        )

        for badge in badges['badges']:
            embed.add_field(name=f"{badge['emoji_icon']} {badge['name']}", value=f"```css\n{badge['desc']}```", inline=False)

        embed = functions.embed_footer(ctx,embed)
        await ctx.send(embed=embed)


    #CMD-ECONSTATS
    @commands.command(aliases=['estats'])
    async def econstats(self, ctx, mention: discord.User = None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        if mention:
            user = mention
        else:
            user = ctx.author

        await initialize_user(user.id)

        stats = await load_stats(user.id)

        embed = discord.Embed(
            title=f"{user}'s Economy Stats",
            colour=discord.Colour.orange()
        )
        
        stats_string = ""
        for activity in stats:  
            for statistic in stats[activity]:
                stat_name = statistic
                if "_" in stat_name:
                    stat_name = stat_name.split("_")
                    stat_name = " ".join(stat_name[:])

                stats_string += f"{stat_name.capitalize()}: `{stats[activity][statistic]}`\n"
            
            embed.add_field(name=activity.capitalize(), value=stats_string, inline=False)
        
        embed.set_thumbnail(url=user.avatar_url)
        embed = functions.embed_footer(ctx, embed)
        await ctx.send(embed=embed)


    #CMD-ECONPROFILE
    @commands.command(aliases=['ep', 'bal', 'balance'])
    async def econprofile(self, ctx, mention: discord.User = None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        if mention:
            user = mention
            await initialize_user(user.id) #don't level up if someone is checking
        else:
            user = ctx.author
            await initialize_user(user.id, ctx)

        data = await load_player_data()
        data = data[str(user.id)]

        if not data['bio']:
            bio = "User hasn't written a bio yet! `.econbio <bio>`"
        else:
            bio = f"```{data['bio']}```"

        embed = discord.Embed(
            title=f"{user}'s Economy Profile",
            colour=discord.Colour.orange(),
            description=f"{bio}"
        )
        
        embed.add_field(name="Stats", value=f"Level: `{data['level']}`\nExp: `{data['exp']}/{data['level_next']}`\nTokens: `{data['tokens']}`\nBoxes opened: `{data['boxes_opened']}`\nKO boost: `{data['ko_boost']}` kills (x{await ko_multiplier(user.id)})", inline=False)

        badge_string = ""
        for badge in data['badges']:
            badge_data = await get_badge_data(badge)
            badge_string += f"{badge_data['emoji_icon']} {badge_data['name']}\n"
        if not badge_string:
            badge_string = "None!"

        embed.add_field(name="Badges", value=badge_string, inline=False)
        embed.set_thumbnail(url=user.avatar_url)
        embed = functions.embed_footer(ctx, embed)

        await ctx.send(embed=embed)


    #CMD-ECONBIO
    @commands.command(aliases=['eb'])
    async def econbio(self, ctx, *bio):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        await initialize_user(ctx.author.id)
        
        bio = str(" ".join(bio[:]))
        if len(bio) > 150:
            return await ctx.send(f"Max bio length exceeded by {len(bio)-150} letters! Max length is `150`.")
        elif not len(bio):
            return await ctx.send("Please enter a bio!\nUsage: `.econbio <bio>`")

        await update_player_data(ctx.author.id, "bio", bio, True)

        await ctx.send(f"{ctx.author}'s bio set to ```{bio}```")


    #CMD-GIVE
    @commands.command()
    @commands.check(functions.is_it_me)
    async def give(self, ctx, mention: discord.User=None, item_id: str=None, amount: int=1):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        if mention:
            user_id = ctx.author.id
        else:
            user_id = mention.id

        await initialize_user(user_id)

        await update_inventory(user_id, item_id, amount, True)


    #CMD-UPDATE_DATA
    @commands.command()
    @commands.check(functions.is_it_me)
    async def update_data(self, ctx, mention: discord.User, key, value, set_=True):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        if mention:
            user_id = ctx.author.id
        else:
            user_id = mention.id

        await initialize_user(user_id)

        await update_player_data(user_id, key, value, set_)


    #CMD-BOXES
    @commands.command()
    async def boxes(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        await initialize_user(ctx.author.id)

        player_data = await load_player_data()
        all_boxes = await return_drops("boxes")

        embed = discord.Embed(
            title="Item Box Store",
            description="`.buy <amount> <box>`\n`.unbox <box>`",
            colour=discord.Colour.orange()
        )

        def sort_by_rarity(list):
            return list['rarity']

        all_boxes.sort(key=sort_by_rarity, reverse=True)

        for box in all_boxes:
            #if not box['purchasable']:
            #    continue
            box_id = await get_id(box['name'])
            embed.add_field(name=f"{box['emoji_icon']} {box['name']} ({player_data[str(ctx.author.id)]['inventory'].count(box_id)})", value=f"*{box['desc']}*\n<:RRtoken:825288414789107762> `{box['tokens']}`", inline=False)
        
        embed.add_field(name="Your balance", value=f"<:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens']}`")

        embed.set_thumbnail(url="https://i.imgur.com/SBxexI1.png")
        embed = functions.embed_footer(ctx, embed)
        await ctx.send(embed=embed)


    #CMD-UPGRADE
    @commands.command()
    async def upgrade(self, ctx, upgrade=None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        await initialize_user(ctx.author.id)
        player_data = await load_player_data()

        if not upgrade:
            return await ctx.send("Include in an upgrade!\n**Usage:** `.upgrade <upgrade>`")

        if upgrade.lower() == "ko":
            if player_data[str(ctx.author.id)]['ko_boost_capacity'] == 35000:
                return await ctx.send("You already have maximum level KO booster capacity upgrade! (35000)")

            if player_data[str(ctx.author.id)]['ko_boost_capacity'] == 1000:
                amount = 5000
                cost = 35000
            elif player_data[str(ctx.author.id)]['ko_boost_capacity'] == 5000:
                amount = 15000
                cost = 60000
            else:
                amount = 35000
                cost = 100000
            
            if player_data[str(ctx.author.id)]['tokens'] >= cost:
                confirm = await Confirm(f"<@{ctx.author.id}>\nYou're about to upgrade maximum KO boost capacity for <:RRtoken:825288414789107762> `{cost}`.\nCurrent capacity: `{player_data[str(ctx.author.id)]['ko_boost_capacity']}`\nCapacity after: `{amount}`\n\nBalance now: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens']}`\nBalance after: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens'] - cost}`\n\nAre you sure?").prompt(ctx)
                
                if confirm:
                    player_data = await load_player_data()
                    if player_data[str(ctx.author.id)]['tokens'] >= cost:
                        await update_player_data(ctx.author.id, "ko_boost_capacity", amount, True)
                        await update_player_data(ctx.author.id, "tokens", -cost, False)

                        await ctx.send(f"{ctx.author} upgraded maximum KO capacity for <:RRtoken:825288414789107762> `{cost}`!\nBalance now: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens']-cost}`")
                else:
                    await ctx.send(f"{ctx.author}'s KO capacity upgrade request canceled.'")
            else:
                await ctx.send(f"You're missing <:RRtoken:825288414789107762> `{cost - player_data[str(ctx.author.id)]['tokens']}`!")
        else:
            await ctx.send("Upgrade not found!")
    
    #CMD-BOOSTERS
    @commands.command()
    async def boosters(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        await initialize_user(ctx.author.id)

        player_data = await load_player_data()
        all_ko = await return_drops("ko")

        embed = discord.Embed(
            title="KO Booster Store",
            description="**The more KO boost you have, the more EXP you receive per kill.**\n`.buy <amount> <booster>`\n`.use <booster>`\n*Note: you don't need to include \"KO Icon - \" when purchasing KO boosters.*",
            colour=discord.Colour.orange()
        )

        def sort_by_rarity(list):
            return list['rarity']

        all_ko.sort(key=sort_by_rarity, reverse=True)

        for ko in all_ko:
            ko_id = await get_id(ko['name'])
            embed.add_field(name=f"{ko['emoji_icon']} {ko['name']} ({player_data[str(ctx.author.id)]['inventory'].count(ko_id)})", value=f"*{ko['desc']}*\n(+{ko['boost']} kills)\n<:RRtoken:825288414789107762> `{ko['tokens']}`", inline=False)

        if player_data[str(ctx.author.id)]['ko_boost_capacity'] == 1000:
            embed.add_field(name="Upgrade maximum capacity!", value="`1000` > `5000` *New max multiplier: x3.5*\n<:RRtoken:825288414789107762> `35,000` `.upgrade ko`")
        elif player_data[str(ctx.author.id)]['ko_boost_capacity'] == 5000:
            embed.add_field(name="Upgrade maximum capacity!", value="`5000` > `15000` *New max multiplier: x8.5*\n<:RRtoken:825288414789107762> `60,000` `.upgrade ko`")
        elif player_data[str(ctx.author.id)]['ko_boost_capacity'] == 15000:
            embed.add_field(name="Upgrade maximum capacity!", value="`15000` > `35000` *New max multiplier: x18.5*\n<:RRtoken:825288414789107762> `100,000` `.upgrade ko`")
        
        embed.set_thumbnail(url="https://i.imgur.com/i75WphN.png")
        embed = functions.embed_footer(ctx, embed)
        await ctx.send(embed=embed)


    #CMD-BEG
    @commands.command()
    @commands.cooldown(10, 60, commands.BucketType.user)
    async def beg(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        await initialize_user(ctx.author.id, ctx)

        chance = random.randint(1, 300)
        if chance < 8:
            item_pool = await get_items_of_rarity(4)
        elif chance < 20:
            item_pool = await get_items_of_rarity(3)
        elif chance < 120:
            item_pool = await get_items_of_rarity(1)
        else:
            item_pool = []
            

        if item_pool:
            item = random.choice(item_pool)
            await update_inventory(ctx.author.id, await get_id(item['name']), 1, True)
            await ctx.send(f"{ctx.author} received {item['emoji_icon']} {item['name']} from a kind stranger!")
        else:
            fail_lines = await load_json("beg_fail")
            dialogue = random.choice(fail_lines)
            await ctx.send(dialogue.format(user=ctx.author))

    @beg.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="You got reported too much!",
                description=f"Timeout for {int(error.retry_after)} seconds.\n||#FixReportSystem||", 
                color=discord.Colour.red()
            )
            embed = functions.embed_footer(ctx, embed)
            await ctx.send(embed=embed)


    #CMD-UNBOX
    @commands.command(aliases=['ub'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def unbox(self, ctx, *box):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        global buy_tax
        to_unbox = False

        await initialize_user(ctx.author.id, ctx)
        player_data = await load_player_data()

        last_box = player_data[str(ctx.author.id)]["last_box"]
        if box:
            box_name = " ".join(box[:])
            box_id = await get_id(box_name)
            box_data = await get_item_data(box_id)
        elif last_box:
            box_id = last_box                        
            box_data = await get_item_data(box_id)
            box_name = box_data['name']

            if box_id in player_data[str(ctx.author.id)]['inventory']: # if player owns the box
                to_unbox = True

        else: return await ctx.send("Please include in a box!\nUsage: `.unbox <box>`\n`.boxes`\n**Tip:** If you open a box, you can open another one of the same box with just `.ub`.")

        if box_id and not to_unbox:
            if box_id in player_data[str(ctx.author.id)]['inventory']: # if player owns the box already
                to_unbox = True
            elif not box_data['purchasable']:
                await ctx.send(f"You ran out of {box_data['emoji_icon']} {box_data['name']}!\n`.boxes`")
                return await update_player_data(ctx.author.id, "last_box", "", True)
            else:
                buy_price = int(box_data['tokens'] * buy_tax)

                if player_data[str(ctx.author.id)]['tokens'] < buy_price:
                    return await ctx.send(f"You're missing <:RRtoken:825288414789107762> `{buy_price - player_data[str(ctx.author.id)]['tokens']}` to buy {box_data['emoji_icon']} {box_name}!\n`.boxes`")
                    
                confirm = await Confirm(f"<@{ctx.author.id}>\nYou're about to buy {box_data['emoji_icon']} {box_data['name']} for <:RRtoken:825288414789107762> `{buy_price}`.\nBalance now: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens']}`\nBalance after: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens'] - buy_price}`\n\nAre you sure?").prompt(ctx)

                if confirm:
                    await update_player_data(ctx.author.id, "last_box", box_id, True)
                    if player_data[str(ctx.author.id)]['tokens'] >= buy_price:
                        await update_player_data(ctx.author.id, "tokens", -buy_price, False)
                        to_unbox = True
                    else:
                        return await ctx.send(f"{ctx.author}'s buy request cancelled - Trying to cheat the system!")
                else:
                    await update_player_data(ctx.author.id, "last_box", "", True)
                    return await ctx.send(f"{ctx.author}'s buy confirmation for {box_data['emoji_icon']} {box_data['name']} canceled!")


        else:
            if not to_unbox:
                return await ctx.send(f"The box `{box_name}` doesn't exist!\n `.boxes`")

        if to_unbox:
            await update_player_data(ctx.author.id, "last_box", box_id, True) # save so you don't need to input box name every time
            await update_inventory(ctx.author.id, box_id, 1, False)

            global reward_instance # I hate doing this, but it works.
            reward_instance[ctx.author.id] = {"rewards": await reward_selection(3, box_data['drops'], box_data['dupes']), "box_data": box_data}
            menu = RewardSelection()
            await menu.start(ctx)

    @unbox.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("Invalid box!\nUsage: `.unbox <box>`\n`.boxes`")
        else:
            raise error
        
    
    #CMD-SELL
    @commands.command()
    async def sell(self, ctx, amount: int=1, *item_name):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        await initialize_user(ctx.author.id)

        if not item_name:
            return await ctx.send("Include in an item!\nUsage: `.sell <amount> <item>`")

        item_name = " ".join(item_name[:])
        item_name = await check_ko_name(item_name)
        
        try:
            amount = int(amount)
            if amount < 1:
                return await ctx.send("Invalid amount!\nUsage: `.sell <amount> <item>`")
        except:
            return await ctx.send("Invalid amount!\nUsage: `.sell <amount> <item>`")

        item_id = await get_id(item_name)
        if item_id:
            player_data = await load_player_data()
            item_data = await get_item_data(item_id)

            if not item_data['sellable']:
                return await ctx.send(f"{item_data['emoji_icon']} {item_data['name']} can't be directly sold!")

            amount_in_inv = await item_count_in_inventory(ctx.author.id, item_id)
            if amount_in_inv > 0:
                if amount > amount_in_inv:
                    amount = amount_in_inv
                global sell_tax
                sell_price = int((item_data['tokens'] * amount) * sell_tax)
                
                old_amount_in_inv = amount_in_inv
                item_string = f"{amount}x {item_data['emoji_icon']} `{item_data['name']}`"
                confirm = await Confirm(f"<@{ctx.author.id}>\nYou're about to sell {item_string} for <:RRtoken:825288414789107762> `{sell_price}`.\nBalance now: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens']}`\nBalance after: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens'] + sell_price}`\n\nAre you sure?").prompt(ctx)
                if confirm:
                    # Sell confirmed
                    # Check if the item count in inventory has changed
                    amount_in_inv = await item_count_in_inventory(ctx.author.id, item_id) 
                    if amount_in_inv == old_amount_in_inv:
                        # Item count is the same
                        await update_inventory(ctx.author.id, item_id, amount, False)
                        await update_player_data(ctx.author.id, "tokens", sell_price, False)
                        
                        await ctx.send(f"{ctx.author} sold {item_string} for <:RRtoken:825288414789107762> `{sell_price}`!\nBalance now: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens']+sell_price}`")
                    else:
                        await ctx.send(f"{ctx.author}'s sell request cancelled - Item count in inventory is different!")
                else:
                    await ctx.send(f"{ctx.author}'s sell confirmation for {item_string} canceled!")
            else:
                return await ctx.send(f"You don't have any {item_data['emoji_icon']} `{item_data['name']}`!")
        else:
            return await ctx.send(f"`{item_name}` doesn't exist!")

        #inv_list = player_data[str(ctx.author.id)]['inventory']

    @sell.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid amount!\nUsage: `.sell <amount> <item>`")
        else:
            raise error

    
    #CMD-SELLALL
    @commands.command()
    async def sellall(self, ctx, category: int=None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        await initialize_user(ctx.author.id)

        player_data = await load_player_data()

        if category:
            if category in (1,2,3,4,5):
                inv = await get_items_of_rarity_inv(ctx.author.id, category)
            else:
                await ctx.send("Invalid rarity!\nRarities are 1, 2, 3, 4, 5.")
        else:
            inv = await load_inventory(ctx.author.id)

        networth = 0
        item_count = 0
        for item in inv:
            if category:
                if item['item']['category'] == "boxes" or not item['item']['sellable']: # GET RID OF BOXES WHEN RARITY SPECIFIED
                    inv.remove(item)
                    continue
            item_count += item['amount']
            networth += item['item']['tokens'] * item['amount']

        if len(inv) == 0:
            return await ctx.send("You don't have anything to sell!")

        global sell_tax
        sell_price = int(networth * sell_tax)

        temp_inv = inv
        if category:
            confirm = await Confirm(f"<@{ctx.author.id}>\nYou're about to sell all of your {category} star items (`{item_count}`) for <:RRtoken:825288414789107762> `{sell_price}`.\nCurrent balance: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens']}`\nBalance after: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens']+sell_price}`\n\nAre you sure?").prompt(ctx)
        else:
            confirm = await Confirm(f"<@{ctx.author.id}>\nYou're about to sell ALL your `{item_count}` items (even boxes) for <:RRtoken:825288414789107762> `{sell_price}`.\nCurrent balance: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens']}`\nBalance after: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens']+sell_price}`\n\nYou can alternatively sell all items of a rarity. `.sellall <rarity>`\n\nAre you sure?").prompt(ctx)

        if confirm:
            if category:
                inv = await get_items_of_rarity_inv(ctx.author.id, category)
                for item in inv: # GET RID OF BOXES WHEN RARITY SPECIFIED
                    if item['item']['category'] == "boxes" or not item['item']['sellable']:
                        inv.remove(item)
                        continue
            else:
                inv = await load_inventory(ctx.author.id)
            if temp_inv == inv:
                if category:
                    for item in inv:
                        if item['item']['category'] == "boxes" or not item['item']['sellable']:
                            continue
                        item_id = await get_id(item['item']['name'])
                        await update_inventory(ctx.author.id, item_id, item['amount'], False)
                    await update_player_data(ctx.author.id, "tokens", sell_price, False)
                    await ctx.send(f"{ctx.author} sold all of their `{item_count}` {category} star items for <:RRtoken:825288414789107762> `{sell_price}`!\nCurrent balance: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens']+sell_price}`")
                else:
                    await update_player_data(ctx.author.id, "inventory", [], True)
                    await update_player_data(ctx.author.id, "tokens", sell_price, False)
                    await ctx.send(f"{ctx.author} sold all of their `{item_count}` items for <:RRtoken:825288414789107762> `{sell_price}`!\nCurrent balance: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens']+sell_price}`")
            else:
                await ctx.send(f"{ctx.author}'s sell confirmation for ALL items canceled! - Inventory different since request.")
        else:
            await ctx.send(f"{ctx.author}'s sell confirmation for ALL items canceled!")


    #CMD-LEADERBOARD
    @commands.command(aliases=['lb'])
    async def leaderboard(self, ctx, board_=None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        await initialize_user(ctx.author.id)

        player_data = await load_player_data()

        def sort_by_exp(list):
            return list['exp']
        
        def sort_by_tokens(list):
            return list['tokens']
            
        def sort_by_boxes_opened(list):
            return list['boxes_opened']

        def sort_by_bubblies(list):
            return list['bubblies']

        board = []
        for user in player_data:
            board.append({'user': user, 'exp': player_data[str(user)]['exp'] + player_data[str(user)]['level_next'], 'tokens': player_data[str(user)]['tokens'], 'boxes_opened': player_data[str(user)]['boxes_opened'], "bubblies": await item_count_in_inventory(user, "drinks:1")})

        if not board_:
            board_ = "EXP"

        if board_.lower() in ("token", "tokens"):
            board_type = "Token balance"
            key = "tokens"
            display_str = "<:RRtoken:825288414789107762> {value}"
            board.sort(reverse=True, key=sort_by_tokens)
        elif board_.lower() in ("boxes", "box"):
            board_type = "Boxes Opened"
            display_str = "<:RNBBox:826478764141576192> {value}"
            board.sort(reverse=True, key=sort_by_boxes_opened)
            key = "boxes_opened"
        elif board_.lower() in ("bubbly", "bubblies"):
            board_type = "Bubbly"
            key = "bubblies"
            display_str = "<:Bubbly:825646215256866817> {value}"
            board.sort(reverse=True, key=sort_by_bubblies)
        else:
            board_type = "EXP"
            key = "exp"
            display_str = "{value} EXP"
            board.sort(reverse=True, key=sort_by_exp)
        
        embed = discord.Embed(
            title=f"{board_type} Leaderboard",
            description="Leaderboards: `boxes`, `tokens`, `exp`, `bubbly`\n`.lb <board>`",
            colour=discord.Colour.orange()
        )

        lb_users = []
        for i in range(5):
            if i == 0:
                leader = await self.client.fetch_user(int(board[i]['user']))
                icon = "<:CheerHost:803753879497998386>"
            else:
                icon = ""
            username = await self.client.fetch_user(int(board[i]['user']))
            embed.add_field(name=f"{i+1}. {username} {icon}", value=display_str.format(value=board[i][key]), inline=False)
            lb_users.append(str(board[i]['user']))

        if str(ctx.author.id) not in lb_users:
            i = 0
            for user in board:
                if str(user['user']) == str(ctx.author.id):
                    break
                i += 1
            embed.add_field(name=f"{i}. {ctx.author}", value=display_str.format(value=board[i][key]), inline=False)

        embed = functions.embed_footer(ctx, embed)
        embed.set_thumbnail(url=leader.avatar_url)
        await ctx.send(embed=embed)


    #CMD-USE
    @commands.command()
    async def use(self, ctx, amount: int=1, *item_name):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        await initialize_user(ctx.author.id)

        if not item_name:
            return await ctx.send("Include in an item!\nUsage: `.use <amount> <item>`")

        item_name = " ".join(item_name[:])

        # no need to type "ko icon -" thanks to this code 
        item_name = await check_ko_name(item_name)

        try:
            amount = int(amount)
            if amount < 1:
                return await ctx.send("Invalid amount!\nUsage: `.use <amount> <item>`")
        except:
            return await ctx.send("Invalid amount!\nUsage: `.use <amount> <item>`")

        item_id = await get_id(item_name)
        item_data = await get_item_data(item_id)
        item_string = f"{item_data['emoji_icon']} {item_data['name']}"

        if not item_id:
            return await ctx.send(f"`{item_name}` doesn't exist!")

        if not await is_usable(item_id):
            return await ctx.send(f"{item_string} isn't usable yet!")

        player_data = await load_player_data()
        item_in_inv = player_data[str(ctx.author.id)]['inventory'].count(item_id)
        
        if item_in_inv:
            old_iii = item_in_inv # iii = item_in_inv
            if amount > item_in_inv:
                amount = item_in_inv
            
            if item_data['category'] == "ko":
                boost = item_data['boost']*amount
                current_boost = player_data[str(ctx.author.id)]['ko_boost']
                updated_boost = current_boost+boost

                capacity_hit = ""
                if updated_boost > player_data[str(ctx.author.id)]['ko_boost_capacity']:
                    updated_boost = player_data[str(ctx.author.id)]['ko_boost_capacity']
                    capacity_hit = f"\nMaximum capacity hit! (`{player_data[str(ctx.author.id)]['ko_boost_capacity']}`)"

                use_desc = f"This will grant you an EXP boost for +`{boost}` kills!\n**Boost:** `{current_boost}`>`{updated_boost}`{capacity_hit}"

            confirm = await Confirm(f"<@{ctx.author.id}>\nYou're about to use x{amount} {item_string}.\n\n{use_desc}\n\nAre you sure?").prompt(ctx)

            if confirm:
                if old_iii == player_data[str(ctx.author.id)]['inventory'].count(item_id):
                    await update_inventory(ctx.author.id, item_id, amount, False)
                    await update_player_data(ctx.author.id, "ko_boost", updated_boost, True)
                    await ctx.send(f"{ctx.author}'s activated x{amount} {item_string}!\nTags remaining: `{updated_boost}`")
                else:
                    await ctx.send(f"Couldn't use {amount} {item_string} - Trying to cheat the system!")
            else:
                return await ctx.send(f"Usage of x{amount} {item_string} canceled!")
        else:
            return await ctx.send(f"You don't have any {item_data['emoji_icon']} {item_data['name']}!")

    @use.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid amount!\nUsage: `.use <amount> <item>`")
        else:
            raise error


    #CMD-BUY
    @commands.command()
    async def buy(self, ctx, amount: int=1, *item_name):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        await initialize_user(ctx.author.id)

        if not item_name:
            return await ctx.send("Include in an item!\nUsage: `.buy <amount> <item>`")

        item_name = " ".join(item_name[:])

        # no need to type "ko icon -" thanks to this code 
        item_name = await check_ko_name(item_name)
        
        try:
            amount = int(amount)
            if amount < 1:
                return await ctx.send("Invalid amount!\nUsage: `.buy <amount> <item>`")
        except:
            return await ctx.send("Invalid amount!\nUsage: `.buy <amount> <item>`")

        item_id = await get_id(item_name)
        if item_id:
            player_data = await load_player_data()

            item_data = await get_item_data(item_id)

            if not item_data['purchasable']:
                return await ctx.send(f"{item_data['emoji_icon']} {item_data['name']} is not purchasable!")

            global buy_tax
            buy_price = int((item_data['tokens'] * amount) * buy_tax)

            if buy_price > player_data[str(ctx.author.id)]['tokens']:
                return await ctx.send(f"You're missing <:RRtoken:825288414789107762> `{buy_price - player_data[str(ctx.author.id)]['tokens']}`!")
                
            item_string = f"{amount}x {item_data['emoji_icon']} `{item_data['name']}`"

            confirm = await Confirm(f"<@{ctx.author.id}>\nYou're about to buy {item_string} for <:RRtoken:825288414789107762> `{buy_price}`.\nBalance now: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens']}`\nBalance after: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens'] - buy_price}`\n\nAre you sure?").prompt(ctx)
            if confirm:
                if buy_price <= player_data[str(ctx.author.id)]['tokens']:
                    await update_inventory(ctx.author.id, item_id, amount)
                    await update_player_data(ctx.author.id, "tokens", -buy_price, False)
                    
                    await ctx.send(f"{ctx.author} bought {item_string} for <:RRtoken:825288414789107762> `{buy_price}`!\nBalance now: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens']-buy_price}`")
                    return True
                else:
                    await ctx.send(f"{ctx.author}'s buy request cancelled - Trying to cheat the system!")
                    return False
            else:
                await ctx.send(f"{ctx.author}'s buy confirmation for {item_string} canceled!")
                return False
        else:
            return await ctx.send(f"`{item_name}` doesn't exist!")
            return False

        #inv_list = player_data[str(ctx.author.id)]['inventory']

    @buy.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid amount!\nUsage: `.buy <amount> <item>`")
        else:
            raise error


    #CMD-DAILY
    @commands.command()
    async def ddaily(self, ctx):
        await initialize_user(ctx.author.id)

        player_data = await load_player_data()
        challenges = await load_challenges()

        today = date.today()
        utc = datetime.utcnow()
        today_date = today.strftime("%d/%m/%Y")
        utc_time = utc.strftime('%H.%M')
        dailies = []

        if player_data[str(ctx.author.id)]['last_daily_date'] != today_date:
            for i in range(3):
                challenge = 0
                while not challenge:
                    challenge = random.randint(2, len(challenges)-1)
                    if {"id": challenge, "progression": 0} not in dailies:
                        dailies.append({"id": challenge, "progression": 0})
                    else:
                        challenge = 0

            await update_player_data(ctx.author.id, "last_daily_date", today_date, True)
            await update_player_data(ctx.author.id, "last_daily_time", utc_time, True)
            await update_player_data(ctx.author.id, "daily_challenges", dailies, True)

        if not dailies:
            dailies = player_data[str(ctx.author.id)]['daily_challenges']
            
        embed = discord.Embed(
            title="Daily challenges!",
            description="WIP! THEY DON'T WORK YET!",
            colour = discord.Colour.orange()
        )

        i = 0
        for task in dailies:
            if task['progression'] >= challenges[task['id']]['requirement']:
                pass

            i += 1
            item_data = await get_item_data(challenges[task['id']]['reward'])
            embed.add_field(name=f"{i}. {challenges[task['id']]['name']}", value=f"**Progression: {task['progression']}/{challenges[task['id']]['requirement']}**\n**Reward:** x{challenges[task['id']]['amount']} {item_data['emoji_icon']} `{item_data['name']}`", inline=False)

        embed = functions.embed_footer(ctx,embed)
        await ctx.send(embed=embed)

    
    #CMD-DAILY
    @commands.command()
    async def daily(self, ctx):
        await initialize_user(ctx.author.id)

        player_data = await load_player_data()

        today = date.today()
        utc = datetime.utcnow()
        today_date = today.strftime("%d/%m/%Y")
        utc_time = utc.strftime('%H.%M')

        if player_data[str(ctx.author.id)]['last_daily_date'] != today_date:
            await update_inventory(ctx.author.id, "boxes:0", 10, True)
            await update_player_data(ctx.author.id, "tokens", 2500, False)


            await update_player_data(ctx.author.id, "last_daily_date", today_date, True)
            await update_player_data(ctx.author.id, "last_daily_time", utc_time, True)

            await ctx.send(f"<@{ctx.author.id}> claimed 10x <:RNBBox:826478764141576192> `Consumable Box` & <:RRtoken:825288414789107762> `2500`")
        else:
            await ctx.send("Daily rewards claimed! Come back tomorrow!")

    @commands.command()
    @commands.check(functions.is_it_me)
    async def purge_stats(self,ctx):
        player_data = await load_player_data()

        for user in player_data:
            await initialize_user(user)

            player_data[str(user)].pop('stats')

        await save_player_data(player_data)

        await ctx.send("Purged!")


    @commands.command()
    @commands.check(functions.is_it_me)
    async def purge(self, ctx):
        player_data = await load_player_data()

        await ctx.send("Starting to purge!")

        for user in player_data:
            await initialize_user(user)
            print(user)
            #player_data[str(user)]['level'] = 0
            #player_data[str(user)]['level_next'] = 1000
            #player_data[str(user)]['inventory'] = ["drinks:1", "drinks:1", "drinks:1", "boxes:0", "boxes:0", "boxes:0", "boxes:0", "boxes:0", "boxes:0", "boxes:0", "boxes:0", "boxes:0", "boxes:0"]
            player_data[str(user)]['stats'] = {}

            player_data[str(user)]['level'] = 0
            player_data[str(user)]['level_next'] = 10
            player_data[str(user)]['exp'] = 0

            #inv = await load_inventory(user)

            #networth = 0
            #for item in inv:
                #networth += item['item']['tokens'] * item['amount']

            #player_data[str(user)]['tokens'] = int(networth * 0.3 + player_data[str(user)]['tokens'] * 0.5)

        await save_player_data(player_data)
        await ctx.send("Purged")

    
    @commands.command()
    async def gift(self, ctx, amount: int=1, item_name=None, mention: discord.User=None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        if not mention:
            return await ctx.send("Include in an user!\n(Remember to wrap item name inside quotations!)\nUsage: `.gift <amount> \"item\" <mention>`")

        await initialize_user(ctx.author.id)
        await initialize_user(mention.id)

        if mention.id == ctx.author.id:
            return await ctx.send("Feeling lonely..?")

        if not item_name:
            return await ctx.send("Include in an item!\n(Remember to wrap item name inside quotations!)\nUsage: `.gift <amount> \"item\" <mention>`")
        
        try:
            amount = int(amount)
            if amount < 1:
                return await ctx.send("Invalid amount!\n(Remember to wrap item name inside quotations!)\nUsage: `.gift <amount> \"item\" <mention>`")
        except:
            return await ctx.send("Invalid amount!\n(Remember to wrap item name inside quotations!)\nUsage: `.gift <amount> \"item\" <mention>`")

        item_id = await get_id(item_name)
        if item_id:
            player_data = await load_player_data()
            item_data = await get_item_data(item_id)

            if not item_data['purchasable']:
                return await ctx.send(f"{item_data['emoji_icon']} {item_data['name']} is not purchasable!")

            global buy_tax
            buy_price = int((item_data['tokens'] * amount) * buy_tax)

            if buy_price > player_data[str(ctx.author.id)]['tokens']:
                return await ctx.send(f"You're missing <:RRtoken:825288414789107762> `{buy_price - player_data[str(ctx.author.id)]['tokens']}`!")
                
            item_string = f"{amount}x {item_data['emoji_icon']} `{item_data['name']}`"

            confirm = await Confirm(f"<@{ctx.author.id}>\nYou're about to gift {item_string} for <:RRtoken:825288414789107762> `{buy_price}`.\nBalance now: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens']}`\nBalance after: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens'] - buy_price}`\nGift receivee: {mention}\n\nAre you sure?").prompt(ctx)
            if confirm:
                if buy_price <= player_data[str(ctx.author.id)]['tokens']:
                    await update_inventory(mention.id, item_id, amount)
                    await update_player_data(ctx.author.id, "tokens", -buy_price, False)
                    
                    await ctx.send(f"{ctx.author} bought {item_string} for <:RRtoken:825288414789107762> `{buy_price}`!\nBalance now: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens']-buy_price}`\nGift receivee: <@{mention.id}>\n")
                else:
                    await ctx.send(f"{ctx.author}'s gift request cancelled - Trying to cheat the system!")
            else:
                await ctx.send(f"{ctx.author}'s gift confirmation for {item_string} canceled!")
        else:
            return await ctx.send(f"`{item_name}` doesn't exist!\nPlease wrap the item's name inside quotations!\nUsage: `.gift <amount> \"item\" <mention>`")

        #inv_list = player_data[str(ctx.author.id)]['inventory']

    @gift.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid amount!\n(Remember to wrap item name inside quotations!)\nUsage: `.gift <amount> \"item\" <mention>`")
        else:
            raise error

class Confirm(menus.Menu):
    def __init__(self, msg):
        super().__init__(timeout=30.0, delete_message_after=True)
        self.msg = msg
        self.result = None

    async def send_initial_message(self, ctx, channel):
        return await channel.send(self.msg)

    @menus.button('\N{WHITE HEAVY CHECK MARK}')
    async def do_confirm(self, payload):
        self.result = True
        self.stop()

    @menus.button('\N{CROSS MARK}')
    async def do_deny(self, payload):
        self.result = False
        self.stop()

    async def prompt(self, ctx):
        await self.start(ctx, wait=True)
        return self.result    


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
            item_data = await get_item_data(item)
            stars, sell_price = "", ""
            if item_data['sellable']:
                for i in range(item_data['rarity']):
                    stars += "<:RRStar:825357537209090098> " 
                global sell_tax
                sell_price = f"\n*Sell price: <:RRtoken:825288414789107762> `{int(item_data['tokens'] * sell_tax)}`*"
            elif item_data['wearable']:
                sell_price = f"\n*Min. level: `{item_data['lvl']}`*"
                
            embed.add_field(name=f"{item_data['emoji_icon']} {item_data['name']}", value=f"<:RRtoken:825288414789107762> `{item_data['tokens']}`{sell_price}\n{stars}", inline=True)

        #embed.add_field(name="DEBUG", value=reward_instance.keys())
        #embed.set_footer(text=f"Author id: {self._author_id}")

        box_img_url = reward_instance[self._author_id]['box_data']['img_url']

        embed.set_thumbnail(url=box_img_url)
        embed = functions.embed_footer(ctx, embed)

        return await channel.send(embed=embed)

    async def update_menu(self, reward):
        global reward_instance
        item_id = reward_instance[self._author_id]['rewards'][reward]
        item = await get_item_data(item_id)
        ctx = reward_instance[self._author_id]['ctx']
        player_data = await load_player_data()

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

        stars, inventory_amount = "\n", ""
        if item['category'] != "tokens":
            # Rarity string
            for i in range(item['rarity']):
                stars += "<:RRStar:825357537209090098> " 
            if stars == "\n":
                stars = ""
            else:
                stars += "\n"

            inventory_amount = f"\nx{await item_count_in_inventory(self._author_id, item_id)+1} {item['emoji_icon']} in inventory!"
        else:
            inventory_amount = f"\nBalance: <:RRtoken:825288414789107762> `{player_data[str(ctx.author.id)]['tokens']+item['tokens']}`"

        if item['rarity'] == 5:
            xp = 100
        elif item['rarity'] == 4:
            xp = 20
        elif item['rarity'] == 3:
            xp = 15
        elif item['rarity'] == 2:
            xp = 10
        else:
            xp = 5
        
        xp = int(xp * 1 + (player_data[str(self._author_id)]['level'] * 0.1))
        xp_boost_str = ""
        gear_boost = await cosmetic_multiplier(self._author_id, 'box')
        if not gear_boost == 1:
            extra_xp = int(gear_boost * xp - xp)
            xp_boost_str = f" (+{extra_xp} EXP)"
            xp += extra_xp

        embed.add_field(name=f"{item['emoji_icon']} {item['name']}", value=f"<:RRtoken:825288414789107762> `{item['tokens']}`{stars}\n+{xp} XP gained!{xp_boost_str}{inventory_amount}", inline=False)
        embed.set_footer(text=f"Given to {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=item['img_url'])

        await self.message.edit(embed=embed)
        reward_instance.pop(self._author_id, None)

        await update_inventory(self._author_id, item_id, 1)
        await update_player_data(self._author_id, "boxes_opened", 1, False)

        await update_player_data(self._author_id, "exp", xp, False)

        if item['category'] == "paintball":
            await give_badge(self._author_id, 10)

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
    client.add_cog(Economy(client))