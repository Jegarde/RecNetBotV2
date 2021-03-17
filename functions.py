import requests
import discord
import arrow
import random
import json
from replit import db

img_quality = 720
image_dict = {"Id": None, "ImageName": None, "CheerCount": 0, "CommentCount": 0}

# Global functions
def log(server, user, command):
    print(f'\n{server} > {user} > {command}')
    if command not in db.keys():
        db[command] = 1
    else:
        db[command] += 1
    if "TotalCount" not in db.keys():
        db["TotalCount"] = 1
    else:
        db["TotalCount"] += 1
        

def load(json_f):
    with open(json_f) as json_file:
        loaded_json = json.load(json_file)
        return loaded_json

def save(json_f, data):
    with open(json_f, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def get_date():
    return arrow.now() # current date

def get_utc_time():
    return arrow.utcnow()

def is_it_me(ctx):
    return ctx.author.id == 293008770957836299 # Jegarde's Discord Id

def beta_tester(ctx):
    #user_roles = ctx.author.roles
    #role = discord.utils.find(lambda r: r.name == 'V2 Tester', ctx.guild.roles)
    #is_beta_tester = role in user_roles
    #return is_beta_tester
    return True

def check_account_existence_and_return(username):
    check = requests.get(f"https://accounts.rec.net/account?username={username}").ok
    if check:
        account_id = username_to_id(username)
        username = id_to_username(account_id)
        return {"account_id": account_id, "username": username}
    else: # account doesn't exist
        try:
            check = requests.get(f"https://accounts.rec.net/account/search?name={username}").json()[0]
            account_id = check['accountId']
            username = check['username']
            return {"account_id": account_id, "username": username}
        except:
            print(f"Account not found! ({username})")
            return False

def map_image_data(arg, dict):
    global image_dict
    if image_dict[dict] < arg[dict]:
        image_dict = {"Id": arg['Id'], "ImageName": arg['ImageName'], "CheerCount": arg['CheerCount'], "CommentCount": arg['CommentCount']}
    return arg[dict]

def map_func(arg, dict):
    return arg[dict]

def self_cheers(photos, account_id):
    self_cheers = 0
    for image in photos:
        try:
            if image['CheerCount'] > 0:
                image_cheer_ids = requests.get(f"https://api.rec.net/api/images/v1/{image['Id']}/cheers").json()
                if account_id in image_cheer_ids:
                    print("self cheered!!!") #REMOVETHIS
                    self_cheers += 1
        except:
            continue
    return self_cheers

def image_embed(image_data):
    tagged = get_tagged_accounts_string(image_data, False)

    username = id_to_username(image_data['PlayerId'])
    room_name = id_to_room_name(image_data['RoomId'])
    if room_name:
        room_string = f"\n🚪 [`^{room_name}`](https://rec.net/room/{room_name})\n"
    else:
        room_string = "\n"

    embed=discord.Embed(
        colour=discord.Colour.orange(),
        title=f"Taken by @{username}",
        description=f"🔗 **[RecNet post](https://rec.net/image/{image_data['Id']})**{room_string}<:CheerGeneral:803244099510861885> `{image_data['CheerCount']}` 💬 `{image_data['CommentCount']}`\n📆 `{image_data['CreatedAt'][:10]}` ⏰ `{image_data['CreatedAt'][11:16]} UTX`\n{tagged}"
    )
    embed.set_image(url=f"https://img.rec.net/{image_data['ImageName']}")
    embed.set_author(name=f"{username}'s profile", url=f"https://rec.net/user/{username}", icon_url=id_to_pfp(image_data['PlayerId']))
    return embed

def cheers_in_room():
    images = requests.get("https://api.rec.net/api/images/v4/room/17274336?take=999999").json()
    print(len(images))
    cheers = 0
    image_count = 0
    for image in images:
        cheers += image['CheerCount']
        image_count += 1

    frontpage = requests.get("https://api.rec.net/api/images/v3/feed/global?take=100").json()

    frontpage_count = 0
    for post in frontpage:
        if post['RoomId'] == 17274336:
            frontpage_count += 1
        

    return {"cheers": cheers, "image_count": image_count, "frontpage_count": frontpage_count}


def get_room_json(room, is_id=False):
    try:
        if not is_id:
            room_data = requests.get(f"https://api.rec.net/roomserver/rooms/search?query={room}", timeout=10).json()
            if room_data["TotalResults"] == 0:
                # Room doesn't exist!
                return None

            for x in room_data["Results"]:
                if x["Name"].casefold() == room.casefold():
                    room_id = x["RoomId"]
                    break
        else:
            if requests.get(f"https://api.rec.net/roomserver/rooms/{room}", timeout=10).ok:
                room_id = room
            else:
                return None

        print(room_id)
        room_json = requests.get(f"https://api.rec.net/roomserver/rooms/{room_id}/?include=366").json()

        return room_json
    except:
        return None
        
def get_room_placement(room):
    hot_rooms = requests.get("https://api.rec.net/roomserver/rooms/hot?take=1000").json()["Results"]
    print("get_room_placement")

    placement = 0
    for x in hot_rooms:
        if x["Name"].casefold() == room.casefold():
            return placement+1
        placement += 1
    return "<1000"

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

def id_to_bio(account_id):
    return requests.get(f"https://accounts.rec.net/account/{account_id}/bio").json()["bio"]

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
    photos = requests.get(f"https://api.rec.net/api/images/v4/player/{account_id}?take=1").json()
    if photos:
        return photos[0]
    else:
        return None

def id_to_photos_in(account_id, room):
    photos = id_to_photos(account_id)
    room = get_room_json(room)
    photos_found = []
    if room and photos:
        for image in photos:
            if image['RoomId'] == room['RoomId']:
                photos_found.append(image)
    return photos_found

def get_photo_comments(image_id):
    return requests.get(f"https://api.rec.net/api/images/v1/{image_id}/comments").json()

def id_to_latest_feed(account_id):
    feed = requests.get(f"https://api.rec.net/api/images/v3/feed/player/{account_id}?take=1").json()
    if feed:
        return feed[0]
    else:
        return None

def id_to_oldest_photo(account_id):
    photos = id_to_photos(account_id)
    if photos:
        return photos[len(photos)-1]
    else:
        return None

def id_to_oldest_feed(account_id):
    feed = id_to_feed(account_id)
    if feed:
        return feed[len(feed)-1]
    else:
        return None

def together(account_id, account_id2):
    user1_feed = id_to_feed(account_id)
    found_images = []
    if user1_feed:
        for image in user1_feed:
            if account_id2 in image['TaggedPlayerIds']:
                found_images.append(image)
    return found_images

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

def percentage_increase(starting_value, final_value):
    return ((final_value - starting_value) / starting_value) * 100

def room_embed(room_name, is_json=False, ctx=None):
    if is_json:
        room = room_name
    else:
        room = get_room_json(room_name)
        
    if room:
        is_cached = False
        print("load")
        cached = dict(load("cached_rinfo.json"))
        if str(room['RoomId']) in cached:
            is_cached = True

        r_name = room['Name']
        
        # Roles
        owner_username = id_to_username(room['CreatorAccountId'])
        owner_pfp = id_to_pfp(room['CreatorAccountId'])
        role_count = len(room['Roles'])
        
        # Placement
        placement = get_room_placement(r_name)

        #visitor_cheer_ratio = round((cheers / visitor_count) * 100)
        #visit_visitor_ratio = round((visitor_count / visit_count) * 100)
        
        # Subrooms
        subrooms = ""
        for i in room["SubRooms"]:
            subroom_name = i["Name"]
            subrooms += f"{subroom_name}, "

        # Other
        
        

        # Warning
        custom_warning = room["CustomWarning"]
        if custom_warning:
            custom_warning = f"\n**Custom warning**\n```{custom_warning}```"
        else:
            custom_warning = ""
        supported = ""
        if room["SupportsWalkVR"]:
            supported += " 🏃‍♂️ "
        if room["SupportsTeleportVR"]:
            supported += " <:RRtele:803747393769570324> "
        if room["SupportsVRLow"]:
            supported += " <:OQ1:803932601768476672> "
        if room["SupportsQuest2"]:
            supported += " <:OQ2:803932151971577896> "
        if room["SupportsScreens"]:
            supported += " 🖥️ "
        if room["SupportsMobile"]:
            supported += " 📱 "
        if room["SupportsJuniors"]:
            supported += " 👶 "

        # Tags
        tags = ""
        for i in room["Tags"]:
            tags += "#" + str(i["Tag"]) + " "
        if not tags:
            tags = "None"

        # Score
        avg_score = 0
        score_list = []
        for i in room["Scores"]:
            if not i["VisitType"] == 2:
                score_list.append(i["Score"])
                avg_score += i["Score"]
        avg_score = round(avg_score / len(score_list), 5)

        # stats
        role_count_string = str(len(room['Roles']))
        cheer_count_string = str(room['Stats']['CheerCount'])
        favorite_count_string = str(room['Stats']['FavoriteCount'])
        visitor_count_string = str(room['Stats']['VisitorCount'])
        visit_count_string = str(room['Stats']['VisitCount'])
        score_string = str(avg_score)
        placement_string = str(placement)
        images_shared_string = ""
        last_check = "\n\n**Last check:** `None!`"
        # cached
        if is_cached:
            cached_data = cached[str(room['RoomId'])]

            print("room photo count")
            try:
                if cached_data['ImagesShared'] == 10000:
                    room_photo_count = ">10000"
                else: 
                    room_photo_count = len(get_photos_in_room(room['Name']))
                    if room_photo_count > 9999:
                        room_photo_count = ">10000"
            except:
                pass

            # Role count
            print("Role count")
            if len(cached_data['Roles']) < role_count:
                role_count_string += f" (+{role_count - cached_data['Roles']})"

            # Cheer count
            print("Cheer count")
            if cached_data['Stats']['CheerCount'] < room['Stats']['CheerCount']:
                cheer_count_string += f" (+{room['Stats']['CheerCount'] - cached_data['Stats']['CheerCount']})"

            # Favorite count
            print("Fav count")
            if cached_data['Stats']['FavoriteCount'] < room['Stats']['FavoriteCount']:
                favorite_count_string += f" (+{room['Stats']['FavoriteCount'] - cached_data['Stats']['FavoriteCount']})"
                
            # Visitor count
            print("Visitor count")
            if cached_data['Stats']['VisitorCount'] < room['Stats']['VisitorCount']:
                visitor_count_string += f" (+{room['Stats']['VisitorCount'] - cached_data['Stats']['VisitorCount']})"

            # Visit count
            print("Visit count")
            if cached_data['Stats']['VisitCount'] < room['Stats']['VisitCount']:
                visit_count_string += f" (+{room['Stats']['VisitCount'] - cached_data['Stats']['VisitCount']})"

            # Score
            print("Score count")
            try:
                if cached_data['Score'] < avg_score:
                    score_string += f" (+{round(percentage_increase(cached_data['Score'], avg_score),5)}%)"
            except:
                pass

            # Placement
            print("Placement")
            try:
                if cached_data['Placement'] > placement:
                    print("ye")
                    placement_string += f" (+{cached_data['Placement'] - placement})"
            except:
                pass

            # Images Shared
            print("Images Shared")
            try:
                if type(room_photo_count) is int:
                    if cached_data['ImagesShared'] < room_photo_count:
                        print("ye")
                        images_shared_string += f" (+{cached_data['ImagesShared'] - room_photo_count})"
            except:
                pass

            # Last check
            print("last check")
            try:
                if cached_data['LastCheck']:
                    print("last check confrim")
                    last_check = f"\n\n**Last check:** 📆 `{cached_data['LastCheck'][:10]}` ⏰ `{cached_data['LastCheck'][11:16]} UTC`"
                    
                if cached_data['LastCheckUserId'] == ctx.author.id:
                    last_check += " by you!"
                elif cached_data['LastCheckUserId'] != ctx.author.id:
                    last_check += " by someone else!"
            except:
                pass

        else:
            room_photo_count = len(get_photos_in_room(room['Name']))
            if room_photo_count > 9999:
                room_photo_count = ">10000"

        images_shared_string = str(room_photo_count)
                
        print("embed")
        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title = f"Statistics for ^{r_name}, by @{owner_username}",
            description = f"[🔗 RecNet Page](https://rec.net/room/{r_name})\n\n**Description**\n```{room['Description']}```{custom_warning}\n**Information**\n:calendar: `{room['CreatedAt'][:10]}` ⏰ `{room['CreatedAt'][11:16]} UTX` *(CREATION DATE)*\n<:CheerHost:803753879497998386> `{role_count_string}` *(USERS WITH A ROLE)*\n🚪 `{subrooms}` *(SUBROOMS)*\n<:tag:803746052946919434> `{tags}` *(TAGS)*\n\n**Supported modes**\n{supported}\n\n**Statistics**\n<:CheerGeneral:803244099510861885> `{cheer_count_string}` *(CHEERS)*\n⭐ `{favorite_count_string}` *(FAVORITES)*\n👤 `{visitor_count_string}` *(VISITORS)*\n👥 `{visit_count_string}` *(ROOM VISITS)*\n🔥 `#{placement_string}` *(HOT PLACEMENT)*\n💯 `{score_string}` *(AVG SCORE)*\n🖼️ `{images_shared_string}` *(PICTURES SHARED IN ROOM)*\n🏅 `{room['MinLevel']}` *(MINIMUM LEVEL)*\n{last_check}"
        )
        print("oimg")
        embed.set_image(url=f"https://img.rec.net/{room['ImageName']}?width=720")
        
        print("author")
        embed.set_author(name=f"{owner_username}'s profile", url=f"https://rec.net/user/{owner_username}", icon_url=owner_pfp)

        print("update")
        cached.pop(str(room['RoomId']), None)
        room['Placement'] = placement
        room['Score'] = avg_score
        room['LastCheck'] = str(get_utc_time())
        print(f"Last check: {room['LastCheck']}")
        if ctx:
            room['LastCheckUserId'] = ctx.author.id
        else:
            room['LastCheckUserId'] = None
        print(f"Last check use id: {room['LastCheckUserId']}")
        room['ImagesShared'] = room_photo_count
        cached[str(room['RoomId'])] = room
        print("save")
        save("cached_rinfo.json", cached)

        return embed
    else:
        return None

def id_to_room_name(room_id):
    try:
        room_name = requests.get(f"https://api.rec.net/roomserver/rooms/{room_id}").json()['Name']
    except:
        room_name = None
    return room_name

def get_featured_rooms():
    return requests.get("https://api.rec.net/roomserver/featuredrooms/current").json()["Rooms"]

def get_room_score(room_name):
    room = get_room_json(room_name)
    avg_score = 0
    score_list = []
    for i in room["Scores"]:
        if not i["VisitType"] == 2:
            score_list.append(i["Score"])
            avg_score += i["Score"]
    avg_score = round(avg_score / len(score_list), 5)
    return avg_score

def get_frontpage(amount=5):
    frontpage = requests.get(f"https://api.rec.net/api/images/v3/feed/global?take={amount}").json()
    return frontpage

def get_tagged_accounts_string(post, usernames_only=False):
    tagged = ""
    bulk = "https://accounts.rec.net/account/bulk?"
    if post['TaggedPlayerIds']:
        tagged = "👥 "
        for account_id in post['TaggedPlayerIds']:
            bulk += f"&id={account_id}"

        accounts = requests.get(bulk).json()

        for account in accounts:
            if usernames_only:
                tagged += f"`@{account['username']}` "
            else:
                tagged += f"[`@{account['username']}`](https://rec.net/user/{account['username']}) "

    return tagged

def find_random_bio():
    bio = None
    while bio == None:
        account_id = random.randint(1, 10000000)
        try:
            bio = requests.get(f"https://accounts.rec.net/account/{account_id}/bio").json()["bio"]
        except:
            continue
    return {"account_id": account_id, "bio": bio}

def find_random_account():
    account_id = random.randint(1, 10000000)
    account = None
    while not account:
        try:
            account = requests.get(f"https://accounts.rec.net/account/{account_id}").json()
        except:
            continue
    return account

def find_random_img():
    img_json = None
    while img_json == None:
      random_int = random.randint(1, 18200000)
      response = requests.get(f"https://api.rec.net/api/images/v4/{random_int}")
      if response.ok == False:
            continue
      img_json = response.json()
    return img_json

def find_random_room():
    room = None
    while not room:
        random_int = random.randint(1, 12000000)
        room_data = requests.get(f"https://api.rec.net/roomserver/rooms/{random_int}?include=366")
        if not room_data.ok:
            continue
        else:
            break
    return room_data.json()

def find_random_event():
    events_json = requests.get("https://api.rec.net/api/playerevents/v1?take=1000").json()
    random_int = random.randint(1, len(events_json)-1)
    return events_json[random_int]

def event_search(word):
    events = requests.get(f"https://api.rec.net/api/playerevents/v1/search?query={word}&take=10").json()
    return events

def latest_events():
    events = requests.get("https://api.rec.net/api/playerevents/v1?take=5").json()
    return events

def get_photos_in_room(room_name, amount=10000, return_photos=False):
    room = get_room_json(room_name)
    if room:
        return requests.get(f"https://api.rec.net/api/images/v4/room/{room['RoomId']}?take={amount}").json()
    else:
        return None

def id_to_rooms(account_id):
    return requests.get(f"https://api.rec.net/roomserver/rooms/createdby/{account_id}").json()

def get_bio(account_id):
    # Get someones bio with their account's id
    return requests.get(f"https://accounts.rec.net/account/{account_id}/bio").json()["bio"]

def embed_footer(ctx, embed):
    today = get_date()
    return embed.set_footer(text=f"Requested by {ctx.author.name} - {today.format('MM/DD/YYYY')}", icon_url=ctx.author.avatar_url)

def contains_word(sentence, word):
    return (' ' + word.casefold() + ' ') in (' ' + sentence.casefold() + ' ')

def error_msg(ctx, desc):
    embed=discord.Embed(
        colour=discord.Colour.orange(),
        description = desc
    )
    embed = embed_footer(ctx, embed)
    return embed

def default_embed():
    return discord.Embed(colour=discord.Colour.orange())