import requests
import discord
import arrow
import random

img_quality = 720
image_dict = {"Id": None, "ImageName": None, "CheerCount": 0, "CommentCount": 0}

# Global functions
def log(server, user, command):
    print(f'\n{server} > {user} > {command}')

def get_date():
    return arrow.now() # current date

def is_it_me(ctx):
    return ctx.author.id == 293008770957836299 # Jegarde's Discord Id

def beta_tester(ctx):
    user_roles = ctx.author.roles
    role = discord.utils.find(lambda r: r.name == 'V2 Tester', ctx.guild.roles)
    is_beta_tester = role in user_roles
    return is_beta_tester

def check_account_existence_and_return(username):
    check = requests.get(f"https://accounts.rec.net/account?username={username}").ok
    print(check)
    return_dict = {}
    if check:
        account_id = username_to_id(username)
        username = id_to_username(account_id)
        return_dict["account_id"] = account_id
        return_dict["username"] = username
        print(return_dict)
        return return_dict
    else: # account doesn't exist
        print(f"Account not found! ({username})")
        return False

def map_image_data(arg, dict):
    if image_dict[dict] < arg[dict]:
        image_dict["Id"] = arg["Id"] 
        image_dict["ImageName"] = arg["ImageName"] 
        image_dict["CheerCount"] = arg["CheerCount"] 
        image_dict["CommentCount"] = arg["CommentCount"] 
    return arg[dict]

def map_func(arg, dict):
    return arg[dict]

def id_to_username(account_id):
    # Get and return account data based on id
    return requests.get(f"https://accounts.rec.net/account/{account_id}").json()["username"]

def id_to_account_data(account_id):
    # Get and return account data based on id
    # If account doesn't exist, return None
    return requests.get(f"https://accounts.rec.net/account/{account_id}").json()

def id_to_pfp(account_id, cropped=True, return_link=True):
    account_pfp = id_to_account_data(account_id)["profileImage"]
    if cropped:
        return f"https://img.rec.net/{account_pfp}?cropSquare=true"
    else:
        if return_link:
            return f"https://img.rec.net/{account_pfp}"
        else: 
            return account_pfp

def id_to_banner(account_id, return_link=True):
    try:
        account_banner = id_to_account_data(account_id)["bannerImage"]
        if return_link:
            return f"https://img.rec.net/{account_banner}"
        else: 
            return account_banner
    except:
        return None

def id_to_display_name(account_id):
    return id_to_account_data(account_id)["displayName"]

def id_to_all_cheers(account_id):
    photos = id_to_photos(account_id)
    map_result = list(map(lambda x: map_func(x, "CheerCount"), photos))
    return map_result

def id_to_all_comments(account_id):
    photos = id_to_photos(account_id)
    map_result = list(map(lambda x: map_func(x, "CommentCount"), photos))
    return map_result

def id_to_creation_date(account_id):
    return id_to_account_data(account_id)["createdAt"]  

def id_to_is_junior(account_id):
    return id_to_account_data(account_id)["isJunior"]  

def id_to_latest_photo(account_id):
    return requests.get(f"https://api.rec.net/api/images/v4/player/{account_id}?take=1").json()[0]

def id_to_latest_feed(account_id):
    return requests.get(f"https://api.rec.net/api/images/v3/feed/player/{account_id}?take=1").json()[0]

def id_to_oldest_photo(account_id):
    photos = id_to_photos(account_id)
    return photos[len(photos)-1]

def id_to_oldest_feed(account_id):
    feed = id_to_feed(account_id)
    return feed[len(feed)-1]

def id_to_photos(account_id):
    return requests.get(f"https://api.rec.net/api/images/v4/player/{account_id}?take=100000").json()

def id_to_feed(account_id):
    return requests.get(f"https://api.rec.net/api/images/v3/feed/player/{account_id}?take=100000").json()

def id_to_cheer_stats(account_id):
    global image_dict
    photos = id_to_photos(account_id)

    image_dict = {"Id": None, "ImageName": None, "CheerCount": 0, "CommentCount": 0}
    map_result = map(lambda x: map_image_data(x, "CheerCount"), photos)

    total_cheers = sum(list(map_result))

    return_dict = {"most_cheered": image_dict, "total_cheers": total_cheers}
    return return_dict

def id_to_comment_stats(account_id):
    global image_dict
    photos = id_to_photos(account_id)

    image_dict = {"Id": None, "ImageName": None, "CheerCount": 0, "CommentCount": 0}
    map_result = map(lambda x: map_image_data(x, "CommentCount"), photos)

    total_comments = sum(list(map_result))

    return_dict = {"most_commented": image_dict, "total_comments": total_comments}
    return return_dict

def username_to_id(account_name):
    # Get and return account's id based on name
    return requests.get(f"https://accounts.rec.net/account?username={account_name}").json()["accountId"]

def find_random_bio():
    bio = None
    while bio == None:
        account_id = random.randint(1, 10000000)
        try:
            bio = requests.get(f"https://accounts.rec.net/account/{account_id}/bio").json()["bio"]
        except:
            continue
    return {"account_id": account_id, "bio": bio}

def get_bio(account_id):
    # Get someones bio with their account's id
    return requests.get(f"https://accounts.rec.net/account/{account_id}/bio").json()["bio"]

def embed_footer(ctx, embed):
    today = get_date()
    return embed.set_footer(text=f"Requested by {ctx.author.name} - {today.format('MM/DD/YYYY')}", icon_url=ctx.author.avatar_url)

def error_msg(ctx, desc):
    embed=discord.Embed(
        colour=discord.Colour.orange(),
        description = desc
    )
    embed = embed_footer(ctx, embed)
    return embed

def default_embed():
    return discord.Embed(colour=discord.Colour.orange())