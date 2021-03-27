import functions
import requests
import discord
from discord.ext import commands

def reset_txt(txt):
    print("Reset")
    open(txt, 'w').close()


class Legacy(commands.Cog):
    def __init__(self, client):
        self.client = client

    # LEGACY COMMANDS

    # CMD-SORTBY
    @commands.command()
    @commands.check(functions.beta_tester)
    async def lsortby(self, ctx, profile, mode):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)

        if account:
            photos = functions.id_to_photos(account['account_id'])
            if photos:
                mode = mode.lower()
                reverse_sort = True
                if mode == "cheers":
                    mode = lambda i: i["CheerCount"]
                    file_name = f"Sorted by CHEERS {account['username']}.txt"
                    reverse_sort = True
                elif mode == "comments":
                    mode = lambda i: i["CommentCount"]
                    file_name = f"Sorted by COMMENTS {account['username']}.txt"
                    reverse_sort = True
                elif mode == "oldest":
                    mode = lambda i: i["CreatedAt"]
                    file_name = f"Sorted by OLDEST {account['username']}.txt"
                    reverse_sort = False
                elif mode == "latest":
                    mode = lambda i: i["CreatedAt"]
                    file_name = f"Sorted by LATEST {account['username']}.txt"
                    reverse_sort = True
                else:
                    mode = None
                
                if mode:
                    save_msg = ""
                    sorted_photos = sorted(photos, key = mode, reverse = reverse_sort)
                    with open("temp_txt.txt","w") as text_file:
                        for photo in sorted_photos:
                            save_msg += f"https://rec.net/image/{photo['Id']}\n"
                            save_msg += f"Date: {photo['CreatedAt'][:10]} {photo['CreatedAt'][11:16]} UTC\n"
                            save_msg += f"Cheers: {photo['CheerCount']}\n"
                            save_msg += f"Comments: {photo['CommentCount']}\n"
                            save_msg += "\n"
                            
                        text_file.write(save_msg)
                        
                    with open("temp_txt.txt","rb") as text_file:
                        await ctx.send(file=discord.File(text_file, file_name))
                    reset_txt("temp_txt.txt")
                else:
                    embed = functions.error_msg(ctx, "Invalid mode! Modes are `cheers`, `comments`, `latest`, `oldest`") 
            else:
                embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single picture!") 
        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!") 

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)
        
        
    @lsortby.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username and mode! \nUsage: `.lsortby <user> <latest|oldest|cheers|comments>`")
            
            await ctx.send(embed=embed)
        else:
            pass
    
    # CMD-TOGETHER
    @commands.command()
    @commands.check(functions.beta_tester)
    async def ltogether(self, ctx, user1, user2):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        author = f"<@{ctx.author.id}>"

        user1_account = functions.check_account_existence_and_return(user1)
        user2_account = functions.check_account_existence_and_return(user2)
        if user1_account and user2_account: #if both exist
            user1_feed = functions.id_to_feed(user1_account['account_id'])
            if user1_feed: # if user appears anywhere
                msg = ""
                save_msg = ""
                photos_found = []
                exceeded_limit = False
                cheers = 0
                comments = 0
                together_images = functions.together(user1_account['account_id'], user2_account['account_id'])
                for post in together_images:
                    photos_found.append(post['Id'])
                    msg += f"<https://rec.net/image/{post['Id']}>\n"

                    cheers += post['CheerCount']
                    comments += post['CommentCount']

                    save_msg += f"https://rec.net/image/{post['Id']}\n"
                    save_msg += f"Date: {post['CreatedAt'][:10]} {post['CreatedAt'][11:16]} UTC\n"
                    save_msg += f"Cheers: {post['CheerCount']}\n"
                    save_msg += f"Comments: {post['CommentCount']}\n"
                    save_msg += "\n"

                if photos_found:
                    if len(msg) > 1500:
                        exceeded_limit = True
                        # message exceeded
                        msg = "*Message exceeded Discord's message length limit.*\n\n"
                        with open("temp_txt.txt","w") as text_file:         
                            text_file.write(save_msg)
                        file_name = f"Together ^{user1_account['username']} and {user2_account['username']}.txt"

                    # first pic
                    msg += f"\n**First picture:** https://rec.net/image/{photos_found[len(photos_found)-1]}\n"
                    # latest picture
                    msg += f"**Latest picture:** https://rec.net/image/{photos_found[0]}\n\n"
                    # cheers
                    msg += f"<:CheerGeneral:803244099510861885> `{cheers}` *(CHEERS IN TOTAL)*\n"
                    # comments
                    msg += f"💬 `{comments}` *(COMMENTS IN TOTAL)*\n\n"
                    # results
                    msg += f"*Results:* `{len(photos_found)}`"

                    if exceeded_limit:
                        print("SEND")
                        with open("temp_txt.txt","rb") as text_file:
                            await ctx.send(f"{author}\n{msg}",file=discord.File(text_file, file_name))
                        reset_txt("temp_txt.txt")
                    else:
                        print("what")
                        await ctx.send(f"{author}\n{msg}")

                else: # not found
                    embed = functions.error_msg(ctx, f"Couldn't find any post that features both `@{user1_account['username']}` and `@{user2_account['username']}`!")
                await ctx.send(embed=embed)
            else:
                embed = functions.error_msg(ctx, f"Couldn't find any post that features both `@{user1_account['username']}` and `@{user2_account['username']}`!")
                await ctx.send(embed=embed)

        else: # either doesn't exist
            embed = functions.error_msg(ctx, f"Either `@{user1}` or `@{user2}` don't exist!")
            await ctx.send(embed=embed)

    @ltogether.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in 2 users! Usage: `.ltogether <user1> <user2>`")
            
            await ctx.send(embed=embed)
        else:
            pass

    
    # CMD-TAKENIN
    @commands.command()
    @commands.check(functions.beta_tester)
    async def ltakenin(self, ctx, room, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        author = f"<@{ctx.author.id}>"

        room_data = functions.get_room_json(room)
        if room_data: #if room exists
            account = functions.check_account_existence_and_return(profile)
            if account: # if account exists
                photos = functions.id_to_photos(account['account_id'])
                if photos: # if user has posted anything
                    msg = ""
                    save_msg = ""
                    photos_found = []
                    exceeded_limit = False
                    cheers = 0
                    comments = 0
                    for post in photos:
                        if post['RoomId'] == room_data['RoomId']:
                            photos_found.append(post['Id'])
                            msg += f"<https://rec.net/image/{post['Id']}>\n"

                            cheers += post['CheerCount']
                            comments += post['CommentCount']

                            save_msg += f"https://rec.net/image/{post['Id']}\n"
                            save_msg += f"Date: {post['CreatedAt'][:10]} {post['CreatedAt'][11:16]} UTC\n"
                            save_msg += f"Cheers: {post['CheerCount']}\n"
                            save_msg += f"Comments: {post['CommentCount']}\n"
                            save_msg += "\n"

                    if photos_found:
                        if len(msg) > 1500:
                            exceeded_limit = True
                            # message exceeded
                            msg = "*Message exceeded Discord's message length limit.*\n\n"
                            with open("temp_txt.txt","w") as text_file:         
                                text_file.write(save_msg)
                            reset_txt("temp_txt.txt")
                            file_name = f"Taken in ^{room_data['Name']}, by {account['username']}.txt"

                        # first pic
                        msg += f"\n**First picture in **`^{room_data['Name']}`: https://rec.net/image/{photos_found[len(photos_found)-1]}\n"
                        # latest picture
                        msg += f"**Latest picture in **`^{room_data['Name']}`: https://rec.net/image/{photos_found[0]}\n\n"
                        # cheers
                        msg += f"**Cheers in total:** `{cheers}`\n"
                        # comments
                        msg += f"**Comments in total:** `{comments}`\n\n"
                        # results
                        msg += f"*Results:* `{len(photos_found)}`"

                        if exceeded_limit:
                            print("SEND")
                            with open("temp_txt.txt","rb") as text_file:
                                await ctx.send(f"{author}\n{msg}",file=discord.File(text_file, file_name))
                        else:
                            print("what")
                            await ctx.send(f"{author}\n{msg}")

                    else: # not found
                        embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single picture in `^{room_data['Name']}`!")
                        await ctx.send(embed=embed)
                else:
                    embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single picture!")
                    await ctx.send(embed=embed)
            else:
                embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
                await ctx.send(embed=embed)

        else: # room doesn't exist
            embed = functions.error_msg(ctx, f"Room `{room}` doesn't exist!")
            await ctx.send(embed=embed)

    @ltakenin.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in a room and an user! Usage: `.ltakenin <room> <user>`")
            
            await ctx.send(embed=embed)
        else:
            pass
            

    # CMD-TAKENOF
    @commands.command()
    @commands.check(functions.beta_tester)
    async def ltakenof(self, ctx, of_user, by_user):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        author = f"<@{ctx.author.id}>"

        of_user_account = functions.check_account_existence_and_return(of_user)
        by_user_account = functions.check_account_existence_and_return(by_user)
        if of_user_account and by_user_account: #if both exist
            of_user_feed = functions.id_to_feed(of_user_account['account_id'])
            if of_user_feed: # if user appears anywhere
                msg = ""
                save_msg = ""
                photos_found = []
                exceeded_limit = False
                cheers = 0
                comments = 0
                for post in of_user_feed:
                    if by_user_account['account_id'] == post['PlayerId']:
                        photos_found.append(post['Id'])
                        msg += f"<https://rec.net/image/{post['Id']}>\n"

                        cheers += post['CheerCount']
                        comments += post['CommentCount']

                        save_msg += f"https://rec.net/image/{post['Id']}\n"
                        save_msg += f"Date: {post['CreatedAt'][:10]} {post['CreatedAt'][11:16]} UTC\n"
                        save_msg += f"Cheers: {post['CheerCount']}\n"
                        save_msg += f"Comments: {post['CommentCount']}\n"
                        save_msg += "\n"

                if photos_found:
                    if len(msg) > 1500:
                        exceeded_limit = True
                        # message exceeded
                        msg = "*Message exceeded Discord's message length limit.*\n\n"
                        with open("temp_txt.txt","w") as text_file:         
                            text_file.write(save_msg)
                        file_name = f"Taken of ^{of_user_account['username']}, by {by_user_account['username']}.txt"

                    # first pic
                    msg += f"\n**First picture:** https://rec.net/image/{photos_found[len(photos_found)-1]}\n"
                    # latest picture
                    msg += f"**Latest picture:** https://rec.net/image/{photos_found[0]}\n\n"
                    # cheers
                    msg += f"**Cheers in total:** `{cheers}`\n"
                    # comments
                    msg += f"**Comments in total:** `{comments}`\n\n"
                    # results
                    msg += f"*Results:* `{len(photos_found)}`"

                    if exceeded_limit:
                        print("SEND")
                        with open("temp_txt.txt","rb") as text_file:
                            await ctx.send(f"{author}\n{msg}",file=discord.File(text_file, file_name))
                        reset_txt("temp_txt.txt")
                    else:
                        print("what")
                        await ctx.send(f"{author}\n{msg}")

                else: # not found
                    embed = functions.error_msg(ctx, f"Couldn't find any picture taken by `@{by_user_account['username']}`, that features `@{of_user_account['username']}`")
                    await ctx.send(embed=embed)
            else:
                embed = functions.error_msg(ctx, f"User `@{of_user_account['username']}` isn't tagged in any post!")
                await ctx.send(embed=embed)

        else: # either doesn't exist
            embed = functions.error_msg(ctx, f"Either `@{of_user}` or `@{by_user}` don't exist!")
            await ctx.send(embed=embed)

    @ltakenof.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in 2 users! Usage: `.ltakenof <of_user> <by_user>`")
            
            await ctx.send(embed=embed)
        else:
            pass
            

    # CMD-TAKENOFIN
    @commands.command(aliases=['ltoi'])
    @commands.check(functions.beta_tester)
    async def ltakenofin(self, ctx, of_user, room):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        author = f"<@{ctx.author.id}>"

        of_user_account = functions.check_account_existence_and_return(of_user)
        room_data = functions.get_room_json(room)
        
        if of_user_account:#if both exist
            if room_data:
                of_user_feed = functions.id_to_feed(of_user_account['account_id'])
                if of_user_feed: # if user appears anywhere
                    msg = ""
                    save_msg = ""
                    photos_found = []
                    exceeded_limit = False
                    cheers = 0
                    comments = 0
                    for post in of_user_feed:
                        if room_data['RoomId'] == post['RoomId']:
                            photos_found.append(post['Id'])
                            msg += f"<https://rec.net/image/{post['Id']}>\n"

                            cheers += post['CheerCount']
                            comments += post['CommentCount']

                            save_msg += f"https://rec.net/image/{post['Id']}\n"
                            save_msg += f"Date: {post['CreatedAt'][:10]} {post['CreatedAt'][11:16]} UTC\n"
                            save_msg += f"Cheers: {post['CheerCount']}\n"
                            save_msg += f"Comments: {post['CommentCount']}\n"
                            save_msg += "\n"

                    if photos_found:
                        if len(msg) > 1500:
                            exceeded_limit = True
                            # message exceeded
                            msg = "*Message exceeded Discord's message length limit.*\n\n"
                            with open("temp_txt.txt","w") as text_file:         
                                text_file.write(save_msg)
                            file_name = f"Taken of @{of_user_account['username']}, in ^{room_data['Name']}.txt"

                        # first pic
                        msg += f"\n**First picture:** https://rec.net/image/{photos_found[len(photos_found)-1]}\n"
                        # latest picture
                        msg += f"**Latest picture:** https://rec.net/image/{photos_found[0]}\n\n"
                        # cheers
                        msg += f"**Cheers in total:** `{cheers}`\n"
                        # comments
                        msg += f"**Comments in total:** `{comments}`\n\n"
                        # results
                        msg += f"*Results:* `{len(photos_found)}`"

                        if exceeded_limit:
                            print("SEND")
                            with open("temp_txt.txt","rb") as text_file:
                                await ctx.send(f"{author}\n{msg}",file=discord.File(text_file, file_name))
                            reset_txt("temp_txt.txt")
                        else:
                            print("what")
                            await ctx.send(f"{author}\n{msg}")
                    
                    else: # not found
                        embed = functions.error_msg(ctx, f"Couldn't find any picture taken of `@{of_user_account['username']}` in `^{room_data['Name']}`!")
                        await ctx.send(embed=embed)
            else:
                embed = functions.error_msg(ctx, f"Room `^{room}` doesn't exist!")
                await ctx.send(embed=embed)

        else: # either doesn't exist
            embed = functions.error_msg(ctx, f"User `@{of_user}` doesn't exist!")
            await ctx.send(embed=embed)

    @ltakenofin.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an user and a room! Usage: `.ltakenofin <user> <room>`")
            
            await ctx.send(embed=embed)
        else:
            pass

    
    # CMD-FRONTPAGE
    @commands.command()
    @commands.check(functions.beta_tester)
    async def lfrontpage(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        msg = ""
        frontpage = functions.get_frontpage(5)
        
        for post in frontpage:
            tagged = ""
            if post['TaggedPlayerIds']:
                tagged = "👥 "
                for account_id in post['TaggedPlayerIds']:
                    tagged += f"`@{functions.id_to_username(account_id)}` "
            else: tagged = "👥 None!"


            msg += f"https://rec.net/image/{post['Id']}\n**{functions.id_to_display_name(post['PlayerId'])}** @{functions.id_to_username(post['PlayerId'])}\n🚪 `^{functions.id_to_room_name(post['RoomId'])}`\n<:CheerGeneral:803244099510861885> `{post['CheerCount']}`\n💬 `{post['CommentCount']}`\n{tagged}\n\n"
            
        await ctx.send(msg)
    

def setup(client):
    client.add_cog(Legacy(client))
