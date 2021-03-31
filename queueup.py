import discord
from discord.ext import commands, tasks
import os
import asyncio
from discord.ext.commands import has_permissions, MissingPermissions
import bot_config
from keyvaluemanagement import *
from filemanagement import *
from discord.ext.commands import has_permissions, MissingPermissions
from quickstart import *
import random

interestsfile = "interests.txt"

datadir = "queue/"
channelpairs = datadir + "channelspairs.txt"

spread = spread()

textfiles = [channelpairs] #Ensures these files exist on launch

confirm_emoji = "👍"


#Changing the name of this class should also be reflected in the setup() function at the bottom of the code.
class QueueCog(commands.Cog):
    '''Queue management'''

    def __init__(self, bot):
        self.bot = bot
        self.homeserver = bot_config.Home_Server
        self.reacttojoinCog = bot.get_cog("ReactJoinCog") #ReactJoinCog otherwise
        
        for entry in textfiles:
            try:
                f = open(entry,"r")
                f.close()
            except Exception as e:
                print("Making file: {}".format(entry))
                f = open(entry,"w")
                f.close()
    
    async def userInServer(self,userid,guildid):
        """Returns true if a user is in a specific server. False otherwise."""
        
        guild = await self.bot.fetch_guild(guildid) 
        members = guild.members
        target = await guild.fetch_member(userid)
        print("call details: userid: {}".format(userid))
        print("target: {}".format(target))
        if(target.id == userid):
            return True
        print("Failed loop: Members:\n{}\n\nGuild:\n{}".format(members,guild))
        return False
    
    async def find_role(self, ctx):
        for x in ctx.author.roles:
            if x.name == "Accountabuds":
                return x
        
        return None
        
    #@commands.command()
    @commands.max_concurrency(1,commands.BucketType.user)
    async def join(self,ctx):
        """Initiate joining of the queue."""
        #slight change here 
        #Check if in the home server
        #if not...
        #...Invite and bail.
        """Returns true if a user is in a specific server. False otherwise."""
        guild = await self.bot.fetch_guild(self.homeserver) 
        members = guild.members
        target = await guild.fetch_member(ctx.author.id)
        print("call details: userid: {}".format(ctx.author.id))
        print("target: {}".format(target))
        if(target.id != ctx.author.id): #In server,
            print("Failed loop: Members:\n{}\n\nGuild:\n{}".format(members,guild))
            #Invite to server
            await ctx.send("You're not in my home server, so you'll have to join it first before I can include you.\n Here you go: {}".format(bot_config.Invite_To_Home_Server))
            return #Abort

        #If user is in a group, exit
        for x in ctx.author.roles:
            if x.name == "Accountabuds":
                await ctx.send("You're already in a stable relationship. Don't do this\n")
                return      

        if(findValue(spread, "Queue", ctx.author.id) != None): #If user is in the queue, exit
            await ctx.send("You're already in a queue!\n")
            await ctx.send("If you want to update your queue listing, try {}dropout then rejoin.\n".format(bot_config.pfix))
            return

        if (ctx.message.mentions != []): #If user mentioned someone
            if (ctx.message.mentions[0] == ctx.author): #Only reads first mention
                await ctx.send("You must be lonely, huh?\n") #Exits if user tried to join with themselves
                await ctx.send("Try {}join without arguments.\n".format(bot_config.pfix))
                return

            else:
                userListing = findValue(spread, "Queue", ctx.message.mentions[0].id) 
                if (userListing != None): #Pairs with someone on the list
                    #interests = kvGetValue(queuefile, userListing)
                    await self.forcePair(ctx, ctx.message.mentions[0])
                    return
                else:
                    await ctx.send("You gotta ask for permission before wanting to join with people, buddy.")
                    await ctx.send("We'll put you on the list instead...\n\n")

        #Normal joining if they pass all the checks.
        
        #List interests
        interests = kvGetKeys(interestsfile)
        #this kvGetKeys function comes from keyvaluemanagement.py. It treats a text file like a dictionary.
        
        interestlist = ""
        for interest in interests:
            interestlist += interest+'\n'
        
        statusmessage = await ctx.send("Hi! I'm Accountabuddy. Select one or a few areas you want to be held accountable for and I'll work to pair you with someone also wanting to be held accountable for the same thing.\n\nAvailable communities:\n{}\nPlease enter one or a few!".format(interestlist))

        tries = 2
        
        while tries != 0:
            tries -= 1
        
            #This block waits for a message reply.
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            try:
                newmsg = await self.bot.wait_for('message', check=check,timeout=60)
            except asyncio.TimeoutError:
                await statusmessage.edit(content="Timed out waiting for a reply.")
                tries = 0
                return
        
            #await statusmessage.edit(content="Parsed message: {}".format(newmsg.content))
            
            #Search the response for interests.
            
            readinterests = [] #List of found interests in message
            words = newmsg.content.lower()
            print("words: {}".format(words))
            
            for interest in interests:
                if(interest.lower() in words ): #Inside the list of interests, all lowercase
                    readinterests.append(interest)
            
            if(len(readinterests)==0):#Couldn't parse any interests
                
                if(tries!=0):
                    await ctx.send("Could you try that again? I couldn't pick up anything you said from the list.")
                else: #Give up
                    await ctx.send("I couldn't follow you at all... Try again later!")
                    return
                continue
            else:
                break
            
        """
        
        debugtext = "Parsed interests: {}\n".format(readinterests)
        
        debugtext += "Relations:\n"
        for read in readinterests:
            debugtext += "{}: {}\n".format(read,kvGetValue(interestsfile,read).split("$"))
        
        """
        
        #debugtext = "Here's what I caught:\n\n"
        #for read in readinterests:
            #debugtext += "{}\n".format(read)
        
        #debugtext += "\n **Finding a pair can take a while, and you will be sent a DM confirmation once a match is found.** Sounds good? Then hit the 👍 and I'll add you to the waitlist!"
        
        
        #message = await ctx.send(content=debugtext)
        
        
        ##Add a thumb react to the message and wait for confirmation.
        #await message.add_reaction('👍')
        #def check(reaction, user):
            #return user == ctx.author and str(reaction.emoji) == '👍'
        
        #try:
            #reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        #except asyncio.TimeoutError:
            ##await channel.send('👎')
            #await message.edit(content="Timeout, took to long to respond.")
            #return
        
        #await message.edit(content="Adding to waitlist...")
        
        await self.addToQueue(ctx, ctx.author,readinterests, True)        
        
        pass

    @commands.command()
    async def list(self, ctx):
        """Shows the current queue in text format"""
        users, interests = get_sheet(spread, "Queue")
        if (users == None):
            await ctx.send("There is no one on the list currently.")
            return
        guild = bot_config.Home_Server
        home = self.bot.get_guild(guild)

        for x in range(len(users)):
            await ctx.send("{}: {}\n".format(home.get_member(int(users[x])).name, interests[x]))

    @commands.command()
    async def dropout(self,ctx):
        """Shortcut to remove yourself from the queue"""
        if(findValue(spread, "Queue", ctx.author.id) != None): #Key already exists
            ids, interests = get_sheet(spread, "Queue") #For removing the react
            print("AAAAAAAAA")
            print(interests)
            deleteEntry(spread, "Queue", ctx.author.id) #Easy peasy
            await ctx.send("Removed!")
            self.reacttojoinCog = self.bot.get_cog("ReactJoinCog")
            await self.reacttojoinCog.listUpdate() #Update the list

            for i in range(len(ids)):
                    if ids[i] == ctx.author.id:
                        interests = interests[i].split("$") #Make interests the dropping out user's interests

            interestCog = self.bot.get_cog("ReactInterestCog") #Need react2interest.py
            messages = await interestCog.intchan.history(limit=200).flatten()
            for m in messages: #Looks through messages in #get-started        
                await m.remove_reaction("\U00002705", ctx.author) #Try to remove ✅ from the user
                
        else:
            print("[removeFromQueue] User doesn't exist in the queue. Doing nothing.")
            await ctx.send("You're not on the waitlist!")
    
    """async def removeFromQueue(self, userid:int):
        #Removes a user from the queue
        if(kvGetKey(queuefile, userid) != None): #Key already exists
            kvRemoveKey(queuefile, userid) #Easy peasy
        else:
            print("[removeFromQueue] User doesn't exist in the queue. Doing nothing.")
            pass"""
    
    async def addToQueue(self,ctx, user,interests:list,sendDM=False):
        """Add a user to the queue with these interests. Returns an integer."""
        #Error codes:
        #0 = No error
        #1 = Unable to send DM
          
        #queuefile
        if(findValue(spread, "Queue", user.id) is not None): #Key already exists
            pass #No error... yet.
        
        write_sheet(spread, "Queue", [str(user.id), interests[0]]) #Out we go
        
        if(sendDM==True):
            try:
                await ctx.send("Done! I'll let you know when we find someone else interested.")
                await user.send("Added to queue! I'll send you a message here when a pair is found.\n\nIf you wanna drop the queue, do {}dropout and I will strike you from the waitlist.".format(bot_config.pfix))
            except Exception as e:
                print("Exception in addToQueue Sending DM: {}".format(e))
                return #Unable to send DM
        
        await self.queueUpdate()
        return
    
    async def delete_role(self, ctx):
        #Finds the role, deletes it, and sends everyone with the partner a farewell message
        role = await self.find_role(ctx)
        
        for x in role.members:
            await x.create_dm()
            await x.dm_channel.send("I hope it was a fruitful endeavor.")
        
        print(role.permissions)
        await role.delete()
        return

    @commands.command()
    async def end(self, ctx):
        """Dissolves an Accountabuddy group (only usuable in your pair channel)"""
        #Let's a user quit their current group.

        #Makes it so that the specific channel to be deleted is easy to find.
        if (ctx.channel.category.name.lower() != "pairs"):
            await ctx.send("You can only abandon groups in your meeting room!")
            return

        await self.delete_role(ctx)

        for voice in ctx.channel.category.voice_channels:
            if voice.name.lower() == ctx.channel.name.lower():
                await voice.delete()

        await ctx.channel.delete()
        
        self.reacttointerestCog = self.bot.get_cog("ReactInterestCog")
        await self.reacttointerestCog.listUpdate() #Update the list

    @commands.command(aliases=['pair'],hidden=True) #pair must be aliased because we have a function named pair already
    async def forcePair(self,ctx,user1:discord.User, user2:discord.User = None):
        #Forces two users to pair up. Doesn't remove them from the queue... possible bugs?
        #Curious how the pairs handle multiple users. Hopefully not bad.
        
        #User2 == None:
        #User1 must not be message.author
        #User1 must be in the server
        #Execute pair on author.id and user1
        #else:
        #User1 and User2 must be in the server
        #User1 and User2 must not be equal
        #User1 and User2 must not both be the message.author.id
        #Execute pair on user1 and user2
        
        def checkP(reaction, user):
            return user.id == user2obj.id and str(reaction.emoji) == '👍'
        if(user2==None): #Author and...
            if(user1.id != ctx.author.id and await self.userInServer(user1.id,self.homeserver) == True): #User not caller and in server
                print("user1 is {}".format(user1))
                print("This print statement occurs when user2==None")
                user2=ctx.author
                user1obj = ctx.author
                user2obj = user1
                await ctx.send("Waiting for a reply from {}!".format(user2obj.name))

                mesg = await user2obj.send("If you want to pair with {}, click the '👍'!".format(user1obj.name))

                await mesg.add_reaction('👍')
                
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=checkP)
                    print("You have gotten to the bit where it waits for the reaction")
                except asyncio.TimeoutError:
                    await mesg.edit(content="Timeout, took to long to respond. Pairing aborted.")
                    return
                else:
                    await self.pair(user1.id,user2.id,removeFromQueue=True)
                    return
        else:#User 1 and user 2
            if((user1.id == ctx.author.id and user2.id == ctx.author.id) == False and user1.id != user2.id): #Both users are different and also not both the owner
                if(await self.userInServer(user1.id,self.homeserver) and await self.userInServer(user2.id,self.homeserver)): #Both users in the server
                    print("this appears if user2!=None")
                    await self.pair(user1.id,user2.id,removeFromQueue=False)
                    await ctx.send("Executing pair on {} and {}. Their entires in the queue were not modified.".format(user1.name,user2.name))
                    return    
                    
        await ctx.send("Something went wrong.")
        
    @commands.command(hidden=True) #Not ever used by a user itself
    async def upd(self,ctx):
        self.reacttojoinCog = self.bot.get_cog("ReactJoinCog")
        await self.reacttojoinCog.listUpdate() #Update the list
        print("[upd ran]")
   
    async def queueUpdate(self):
        """Check for pairs and pair them if applicable."""
        #Check for possible pairings in the file.
        #If a pair is found, run pair() from another Cog and remove them from the queue list. They should now be paired!
        
        ids, interestsproxy = get_sheet(spread, "Queue") #Get keys and values from the file
        
        #Split interests into a list of it's interests isntead of a single compressed string
        interests = []
        if(interestsproxy != None):
            for prox in interestsproxy:
                interests.append(prox.split('$'))
            
            for i, userid in enumerate(ids): #Iterate through each user and look for a pair.
                
                #if(userid in askedusers):
                #    continue #If we're already waiting for a response from them. Code for later.
                
                thisinterest = interests[i] #An array of strings
                for j, otherid in enumerate(ids): #Look through other users
                    if(otherid != userid): #Not self
                        otherinterest = interests[j] #Possible partner's interests
                        matches = set(thisinterest) & set(otherinterest)
                        if(len(matches) > 0): #Has a match at all, not complicated
                            #Pair 'em
                            print("[queueUpdate] matches are: {}".format(matches))
                            await self.pair(userid, otherid, interests=matches, removeFromQueue=True)
                            print("[queueUpdate] Paired {} and {}!!".format(userid,otherid))
                            return await self.queueUpdate() #Start from the beginning because our array status has changed.
        
        self.reacttojoinCog = self.bot.get_cog("ReactJoinCog")
        await self.reacttojoinCog.listUpdate() #Update the list
        print("[queueUpdate] is running.")
    
    #TODO: FINISH leaderboard
    @commands.command()
    async def leaderboard(self,ctx):
        """Prints the current leaderboard"""

        leaderboard = get_sheet(spread, "Leaderboard")
        #this kvMakeList function comes from keyvaluemanagement.py.
        
        leaderboardlist = ""
        for score in leaderboard:
            leaderboardlist += score+'\n'

        await ctx.send(self.leaderboardText(leaderboardlist))

    #TODO: STUB FUNCTION
    def leaderboardText(self, leaderboardlist):
        text = leaderboardlist

        return text

    async def pair(self, user1: int, user2:int, interests:list = ['unknown'], removeFromQueue:bool=True):# Pair and remove their entries from the queue
        
        #Create role
        #Create channel
        #Ping the new role or the users
        #Send a final DM to the group's dms
        print("user1 is {}".format(user1))
        user1obj = await self.bot.fetch_user(user1)
        user2obj = await self.bot.fetch_user(user2)

        commonInterests = []
        ids, queueInterests = get_sheet(spread, "Queue")
        print(queueInterests)
        for i in range(len(ids)):
            print(ids[i])
            print(user1)
            print(user2)
            if (int(ids[i]) == int(user1) or int(ids[i]) == int(user2)):
                print(queueInterests[i])
                print("CCCCCCCCCCCC")
                tempInterests = queueInterests[i].split("$")
                for i in range(len(tempInterests)):
                    print(tempInterests[i])
                    commonInterests.append(tempInterests[i])
        print("BBBBBBBBBBBBBBBBB")
        print(commonInterests)
        interestCog = self.bot.get_cog("ReactInterestCog") #Need react2interest.py
        messages = await interestCog.intchan.history(limit=200).flatten()
        for m in messages: #Looks through messages in #get-started
            #Try to remove ✅ from the two paired users
            for interest in commonInterests:
                if (interest == m.content):
                    await m.remove_reaction("\U00002705", user1obj) 
                    await m.remove_reaction("\U00002705", user2obj) 

        await user1obj.send("You've been paired with {}!".format(user2obj.name))
        await user2obj.send("You've been paired with {}!".format(user1obj.name))
        
        print("[pair] users are into {}".format(interests))
        #Still need to make channel and role ties
        
        await self.giveWorkspace(user1,user2,interests) #Create role and channel
        
        if(removeFromQueue==True):
            if(int(user1) != None):
                deleteEntry(spread, "Queue", int(user1))
                deleteEntry(spread, "Queue", int(user2))

    #Give a workspace for two pairbuds to chitchat. Saves ID of channel and it's ID to file.
    async def giveWorkspace(self,user1:int,user2:int,interests:list=['Unknown']):
        #Create a channel, create a role, give that role to two people, save the Channel and ID pair to file, ping both users.
        
        #interests = list(interests)

        home = self.bot.get_guild(self.homeserver)
        channel_name = home.get_member(int(user1)).name + "-" + home.get_member(int(user2)).name 

        role = await self.makeRole(users=[user1,user2]) #Fetch role and give it to the two peeps
        channel = await self.makeRoom(role.id, channel_name)
        
        interestsline = "" #Format current interests given
        if(isinstance(interests,str)): #String, so just add.
            interestsline = interests+"."
        else:
            if(len(interests)==1):
                try:
                    interestsline = interests[0]+'.'
                except Exception as e:
                    interestsline = "."
            elif(len(interests) > 1):
                for i, thing in enumerate(interests): #Iterate with an integer
                    if((i+1) == len(interests)): #Last entry
                        interestsline += " and {}.".format(thing)
                    elif((i+2) == len(interests)): #Second to last entry
                        interestsline += "{} ".format(thing)
                    else: #Anything else (3+ entries)
                        interestsline += "{}, ".format(thing)
        
        await channel.send("<@{}> and <@{}>, here's your private chatroom! You two were both interested in {}\nHave a conversation and say hi! If you want to unpair, use **{}end** to finish your conversation.\n".format(user1,user2,interestsline,bot_config.pfix,bot_config.pfix))

        await self.talk_room(role.id, channel_name)
    
    """
    #TODO: FINISH SELF.HELPTEXT()
    @commands.command()
    async def helpme(self,ctx):
        #Prints help.
        
        await ctx.send(self.helptext())
    
    #TODO: STUB FUNCTION
    def helptext(self):
        pf = bot_config.pfix
        text = pf+"join - Join a queue and get paired"
        
        return text
    """
    
    def getColor(self):
        return random.randint(0x7F7F7F, 0xFFFFFF) #50-100 brightness for each channel, so the color stays bright
    
    #Creates a new role and assigns it to an Accountabuddy pair
    #Logan: I've added optional list support and made a color maker function above.
    async def makeRole(self, user1:int=-1, users:list=[]):#, user2: int):
        home = self.bot.get_guild(self.homeserver)
        #role = await home.create_role(name = "Accountabuds", color = discord.Color(0x0000ff))
        role = await home.create_role(name = "Accountabuds", color = discord.Color(self.getColor()))
        if(len(users)==0):#No members in bulk list
            await home.get_member(user1).add_roles(role)
        else: #Members in list
            for user in users:
                print("User check: {}".format(user))
                member = await home.fetch_member(user)
                print("Member fetch name: {}".format(member.name))
                await member.add_roles(role)
        #await home.get_member(user2).add_roles(role)
        return role

    #Creates a text channel only users with a certain role can access
    async def makeRoom(self, roleid: int, name = "meeting room"):
        home = self.bot.get_guild(self.homeserver)
        category = discord.utils.get(home.categories, name="pairs")
        default = home.default_role
        role = home.get_role(roleid)
        #overwrite = discord.PermissionOverwrite()
        #overwrite.send_messages = True
        #overwrite.read_messages = True
        channel = await category.create_text_channel(name)
        await channel.edit(sync_permissions=False)
        await channel.set_permissions(role, read_messages=True, send_messages=True)
        await channel.set_permissions(default, read_messages=False, send_messages=False)
        return channel

    #Creates a voice channel only users with a certain role can access
    async def talk_room(self, roleid: int, name = "chat room"):
        home = self.bot.get_guild(self.homeserver)
        category = discord.utils.get(home.categories, name="pairs")
        default = home.default_role
        role = home.get_role(roleid)
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = True
        overwrite.read_messages = True
        channel = await category.create_voice_channel(name)
        await channel.edit(sync_permissions=False)
        await channel.set_permissions(role, read_messages=True, send_messages=True, connect=True)
        await channel.set_permissions(default, read_messages=False, send_messages=False, connect=False)
        return channel

    """async def deleteRole(self):
        guild = bot_config.Home_Server
        home = self.bot.get_guild(guild)
        await home.delete_role(name="Accountabud")"""

    #creates functionality for users to change their role color
    @commands.command()
    async def changecolor(self, ctx,*, color):
        """IN PROGRESS: Allows you to change your group color (only for accountable users)"""
        listOfColors = {
                        "blue" : discord.Color.blue(),
                        "teal" : discord.Color.teal(),
                        "darkteal" : discord.Color.dark_teal(),
                        "green" : discord.Color.green(),
                        "darkgreen" : discord.Color.dark_green(),
                        "purple" : discord.Color.purple(),
                        "darkpurple" : discord.Color.dark_purple(),
                        "gold" : discord.Color.gold(),
                        "orange" : discord.Color.orange(),
                        "red" : discord.Color.red(),
                        "darkred" : discord.Color.dark_red()
                      } 
        temp=ctx.message.content.split()
        role=""
        color=""
        for word in temp: 
            if "<@&" in word:
                for letter in word:
                    if letter.isalnum():
                        role= role + letter
            elif bot_config.pfix not in word:
                color = color + word
        for x in ctx.guild.roles:
            if x.id == int(role): 
                if color in listOfColors.keys():
                    role = ctx.message.guild.get_role(int(role))
                    await role.edit(color=listOfColors[color])   
                    return   
        await ctx.send("You do not have that role")
    
    #called by !changecolor @role dark green
   @commands.command()
    async def bl(self,ctx):
        blacklist = get_sheet(spread, "Blacklist")
        #users, blacklisted = get_sheet(spread, "Blacklist") 
        user=ctx.author.id
        userx=ctx.message.mentions[0].id

        index=findValue(spread,"Blacklist", str(user))
        if(index!=None): #if user already in bl userid 
            index+=2
            xvar=getValue(spread,"Blacklist",str(user))
            tvar=xvar[1].split(";")
            if (str(userx) in tvar):
                await ctx.send("This user is already blacklisted")
        
            else: #user not on blacklist, blacklist user 
                #add userx to black list column 
                editValue(spread,"Blacklist",str(user),1,str(userx),True)
                await ctx.send ("User has been blacklisted")
        else: #add userx to black list column 
            write_sheet(spread, "Blacklist", [str(user), str(userx)])
            await ctx.send ("User has been blacklisted")

    @commands.command()
    async def rbl(self, ctx):
        blacklist = get_sheet(spread, "Blacklist")
        #users, blacklisted = get_sheet(spread, "Blacklist")
        user=ctx.author.id
        userx= ctx.message.mentions[0].id

        index=findValue(spread,"Blacklist", str(user))
        if(index!=None): #if user already in bl userid 
            xvar=getValue(spread,"Blacklist", str(user))
            tvar=xvar[1].split(";")
            if (len(tvar) == 1):
                deleteEntry(spread, "Blacklist", str(user))
            elif (str(userx) in tvar):
                tstring=""
                for blocked in tvar:
                    if blocked==str(userx):
                        tvar.remove(blocked)
                    else:
                        if tstring == "":
                            tstring=tstring+blocked
                        else:
                            tstring=";"+tstring+blocked 
                editValue(spread,"Blacklist",str(user),1,tstring,False)
                await ctx.send ("User has been removed from your blacklist")
            else: 
                await ctx.send("This user is not on your blacklist")
        else: 
            await ctx.send("You don't have anyone blacklisted") 
   
    
  
    
    @commands.command()
    async def li(self, ctx):
        """
        This lists all interests currently catalogued.
        """
        interests = get_sheet(spread, "Interests")
        #this kvGetKeys function comes from keyvaluemanagement.py. It treats a text file like a dictionary.
        
        interestlist = ""
        for interest in interests:
            interestlist += interest+'\n'
        await ctx.send(interestlist)

    """    
    @commands.command()
    async def addgoal(self, ctx): # Need to remove the pfix and command from entry
        temp = kvGetKeys(goalsfile);
        splitmess = ctx.message.content.split(); # splits string by white spaces
        mess = ""; 
        try:
            i = temp.index(str(ctx.author.id));
            mess = kvGetValue(goalsfile, str(ctx.author.id))
            for word in splitmess: # ignores first word in message because we know it's just the command and is unneeded.
                if word != splitmess[0]:
                    mess = mess + " " + word; # Places words into the list
            removeFromList(goalsfile, str(ctx.author.id));
            addToList(goalsfile, str(ctx.author.id) + seperator + mess + ";");
        except ValueError: # Value not found
            for word in splitmess: # ignores first word in message because we know it's just the command and is unneeded.
                if word != splitmess[0]:
                    mess = mess + " " + word; # Places words into the list
            addToList(goalsfile, str(ctx.author.id) + seperator + mess + ";");
        except Exception as e:
            print("Exception detected: []".format(e));

    @commands.command()
    async def showgoals(self, ctx): # Need to separate and send line by line
        temp = kvGetKeys(goalsfile);
        try:
            i = temp.index(str(ctx.author.id));
            splitmess = ctx.message.content.split(); # splits string by white spaces
            #for(word in splitmess): # ignores first word in message because we know it's just the command and is unneeded.
            #    if word == ""; # checks to see if any additional parameters were passed.
            mess = kvGetValue(goalsfile, ctx.author.id); # Get user's goals
            mess = mess.split("; "); # Separate goals
            for goal in mess:
                # This space is used to sort through the separated goals to see if any are tagged
                    # This means any that are tagged for completion, past tasks, recurring tasks, etc.
                await ctx.send(goal);
        except ValueError:
            await ctx.send("You aren't on the list");

        #ctx.send(interestlist);
    """
    
    @commands.command()
    async def tutorial(self,ctx):
        await ctx.send("Hi! Since this is your first time using accountabuddy, I've prepared a quick tutorial to get you on your way to self improvement.\nThe first and most important thing to do is determine what you want to work on! We have a varied selection of topics our users focus on, so try to find one of the following that fits your purpose, or is somewhat close to your purpose (if you want to try a paleo diet, dieting is the category you would want). Our categories are-\nJogging\nFrisbee Golf\nStudyHabits\nPizza\nBurgers\nSave Money\nMeditate\nReading\nLearn a Language\nSleep\nLearn to cook\nRunning\nImprove Concentration\nSocial Media Detox\nEarn More Money\nPractice Guitar\nDieting\nAccountabuddy\nWhen you have one of these you would like to work with someone else to improve at, the next thing you'll want to do is try and find someone with the same general improvement area! You're going to use a text command, where you will type !join followed by a space, and then your category of interest- as an example, lets use dieting. So, to start, I would type !join dieting. Once you do this, you will be on your way to helping someone else be accountable!")

    @commands.Cog.listener()
    #@commands.check(processable) #check doesn't work in events, only commands
    async def on_raw_reaction_add(self, payload):
        
        #This listener is different and will catch all reacts, even reacts that occurr on messages that aren't in the cache.
        #This is because messages can persist across bot restarts in this case. It uses a Payload object.
        
        
        if(payload.user_id == self.bot.user.id): #The bot made this react, ignore
            return print("[react2join] Bot made react, ignoring.")
        if(payload.guild_id is None):#None guild_ids are in DMs, ignore
            return print("[react2join] DM reaction, ignoring.")
        if(payload.event_type == "REACTION_REMOVE"):#Reaction removed, ignore.
            return print("[react2join] Reaction was removed, not added, ignoring.")
        if(payload.channel_id != 811364449881161786): #Not the welcome channel, ignore.
            return print("[react2join] Not in the welcome channel, ignoring.")
        

        if(payload.emoji.name == confirm_emoji): #User confirmed to read the message
            
            for role in payload.member.guild.roles:
                if (role.name == "member"):
                    member = role

            for role in payload.member.roles:
                if (role == member):
                    return print("They've already acknowledged the rules")

            await payload.member.add_roles(member)
        
        return


    @commands.command(aliases=['help'])
    async def help_command(self, ctx):
        await ctx.send("""
    Useful Commands:
        
    **{0}abandon**
    Abandon a pairing
    
        **{0}dropout** 
        Drop from a queue

    **{0}help**
        Shows this message

    **{0}list**
        Displays the interests that you are currently queued for.

    **{0}tutorial**
        Displays the tutorial for using Accountabuddy. 
        This is useful if you're new to Accountabuddy. 

    **{0}daily**
        Initiates daily check-in from Accountabuddy

    **{0}stop**
        Stops daily check-in
    """.format(bot_config.pfix))

def setup(bot):
    bot.add_cog(QueueCog(bot))
