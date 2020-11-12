import discord
from discord.ext import commands, tasks
import os
import asyncio
from discord.ext.commands import has_permissions, MissingPermissions
import bot_config
from keyvaluemanagement import *
from filemanagement import *
from discord.ext.commands import has_permissions, MissingPermissions
import random

interestsfile = "interests.txt"
leaderboardfile = "leaderboard.txt"
datadir = "queue/"
queuefile = datadir + "userqueue.txt"
channelpairs = datadir + "channelspairs.txt"

textfiles = [queuefile, channelpairs] #Ensures these files exist on launch


#Changing the name of this class should also be reflected in the setup() function at the bottom of the code.
class QueueCog(commands.Cog):
    '''Queue management'''

    def __init__(self, bot):
        self.bot = bot
        self.homeserver = bot_config.Home_Server
        
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
        
    @commands.command()
    async def join(self,ctx):
        """Initiate joining of the queue."""
        
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
        for x in ctx.me.roles:
            if x.name == "Accountabuds":
                await ctx.send("You're already in a stable relationship. Don't do this\n")
                return      

        if (ctx.message.mentions != []): #If user mentioned someone
            if (ctx.message.mentions[0] == ctx.author): #Only reads first mention
                await ctx.send("You must be lonely, huh?\n") #Exits if user tried to join with themselves
                await ctx.send("Try {}join without arguments.\n".format(bot_config.pfix))
                return

            else:                    
                userListing = kvGetKey(queuefile, ctx.message.mentions[0].id) 
                if (userListing != None): #Pairs with someone on the list
                    interests = kvGetValue(queuefile, userListing)
                    await self.pair(ctx.author.id, ctx.message.mentions[0].id, interests)
                    return
                else:
                    await ctx.send("You gotta ask for permission before wanting to join with people, buddy.")
                    if(kvGetKey(queuefile, ctx.author.id) != None): #If user is in the queue, exit
                        await ctx.send("We're not putting you on the list twice, so seeya.")
                        return
                    else:
                        await ctx.send("We'll put you on the list instead...\n\n")
        else: #They didn't mention anyone
            if(kvGetKey(queuefile, ctx.author.id) != None): #If user is in the queue, exit
            
                await ctx.send("You can't pair up with yourself!\n")
                await ctx.send("If you want to update your queue listing, try {}update instead.\n".format(bot_config.pfix))
                return

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
        
        debugtext = "Here's what I caught:\n\n"
        for read in readinterests:
            debugtext += "{}\n".format(read)
        
        debugtext += "\n **Finding a pair can take a while, and you will be sent a DM confirmation once a match is found.** Sounds good? Then hit the 👍 and I'll add you to the waitlist!"
        
        
        message = await ctx.send(content=debugtext)
        
        
        #Add a thumb react to the message and wait for confirmation.
        await message.add_reaction('👍')
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '👍'
        
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            #await channel.send('👎')
            await message.edit(content="Timeout, took to long to respond.")
            return
        
        await message.edit(content="Adding to waitlist...")
        
        result = await self.addToQueue(ctx.author,readinterests,True)
        
        if(result == 0):
            await message.edit(content="Done!")
        if(result == 1): #Can't send DM
            await message.edit(content="Can't send a DM to you, so I couldn't put you on the waitlist.")
        
        pass

    """
    @commands.command()
    async def show(self, ctx):
        #TODO:Write a kv command that gets the whole queue and pastes it
        #ctx.send("")
    """

    @commands.command()
    async def list(self, ctx):
        
        users = kvGetKeys(queuefile)
        if (users == []):
            await ctx.send("There is no one on the list currently.")
            return
        interests = kvGetValues(queuefile)
        guild = bot_config.Home_Server
        home = self.bot.get_guild(guild)

        for x in range(len(users)):
            await ctx.send("{}: {}\n".format(home.get_member(int(users[x])).name, interests[x]))

    #TODO Make a command that can manually pair with a user

    @commands.command()
    async def dropout(self,ctx):
        if(kvGetKey(queuefile, ctx.author.id) != None): #Key already exists
            kvRemoveKey(queuefile, ctx.author.id) #Easy peasy
            await ctx.send("Removed!")
        else:
            print("[removeFromQueue] User doesn't exist in the queue. Doing nothing.")
            await ctx.send("You're not on the waitlist!")
    
    async def removeFromQueue(self, userid:int):
        """Removes a user from the queue."""
        if(kvGetKey(queuefile, userid) != None): #Key already exists
            kvRemoveKey(queuefile, userid) #Easy peasy
        else:
            print("[removeFromQueue] User doesn't exist in the queue. Doing nothing.")
            pass
    
    
    async def addToQueue(self,user,interests:list,sendDM=False):
        """Add a user to the queue with these interests. Returns an integer."""
        #Error codes:
        #0 = No error
        #1 = Unable to send DM
        
        
        #queuefile
        if(kvGetKey(queuefile, user.id) is not None): #Key already exists
            pass #No error... yet.
        
        kvSetValue(queuefile, user.id,"$".join(interests)) #Out we go.
        
        if(sendDM==True):
            try:
                await user.send("Added to queue! I'll send you a message here when a pair is found.\n\nIf you wanna drop the queue, do {}dropout and I will strike you from the waitlist.".format(bot_config.pfix))
            except Exception as e:
                print("Exception in addToQueue Sending DM: {}".format(e))
                return 1 #Unable to send DM
                
        
        
        await self.queueUpdate()
        return 0
    
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
    async def abandon(self, ctx):
        #Let's a user quit their current group.

        #Makes it so that the specific channel to be deleted is easy to find.
        if (ctx.channel.category.name.lower() != "pairs"):
            await ctx.send("You can only abandon groups in your meeting room!")
            return

        await self.delete_role(ctx)

        await ctx.channel.delete()

    @commands.command()
    async def talk(self, ctx):
        #Lets a user make a voice channel

        #Makes it so that the VC can only be made in a pair room
        if (ctx.channel.category.name.lower() != "pairs"):
            await ctx.send("You can only create talk rooms within your own room!")
            return
        
        home = self.bot.get_guild(self.homeserver)
        category = discord.utils.get(home.categories, name="pairs")
        
        #Prevents two chat rooms
        for x in category.voice_channels:
            if (x.name == ctx.channel.name):
                await ctx.send("You can't create two talk rooms!")
                return

        role = await self.find_role(ctx)
        await self.talk_room(role.id, ctx.channel.name)

    
    @commands.command(aliases=['pair'],hidden=True) #pair must be aliased because we have a function named pair already
    @commands.has_permissions(ban_members=True)
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
        
        
        if(user2==None): #Author and...
            if(user1.id != ctx.author.id and await self.userInServer(user1.id,self.homeserver) == True): #User not caller and in server
                await self.pair(ctx.author.id,user1.id,removeFromQueue=False)
                await ctx.send("Executing pair on {} and {}. Their entires in the queue were not modified.".format(ctx.author.name,user1.name))
                return
        else:#User 1 and user 2
            if((user1.id == ctx.author.id and user2.id == ctx.author.id) == False and user1.id != user2.id): #Both users are different and also not both the owner
                if(await self.userInServer(user1.id,self.homeserver) and await self.userInServer(user2.id,self.homeserver)): #Both users in the server
                    await self.pair(user1.id,user2.id,removeFromQueue=False)
                    await ctx.send("Executing pair on {} and {}. Their entires in the queue were not modified.".format(user1.name,user2.name))
                    return
        await ctx.send("Something went wrong.")
        
        
    
    async def queueUpdate(self):
        """Check for pairs and pair them if applicable."""
        #Check for possible pairings in the file.
        #If a pair is found, run pair() from another Cog and remove them from the queue list. They should now be paired!
        
        ids, interestsproxy = kvGetKeysValues(queuefile) #Get keys and values from the file
        
        #Split interests into a list of it's interests isntead of a single compressed string
        interests = []
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
                        await self.pair(userid, otherid, interests=matches, removeFromQueue=True)
                        print("[queueUpdate] Paired {} and {}!!".format(userid,otherid))
                        return await self.queueUpdate() #Start from the beginning because our array status has changed.
        
        print("[queueUpdate] is running.")
    
    #TODO: FINISH leaderboard
    @commands.command()
    async def leaderboard(self,ctx):
        #prints the leaderboard

        leaderboard = kvMakeList(leaderboardfile)
        #this kvMakeList function comes from keyvaluemanagement.py.
        
        leaderboardlist = ""
        for score in leaderboard:
            leaderboardlist += score+'\n'

        await ctx.send(self.leaderboardText(leaderboardlist))

    #TODO: STUB FUNCTION
    def leaderboardText(self, leaderboardlist):
        text = leaderboardlist

        return text

    
    async def pair(self, user1: int, user2:int, interests:list = [], removeFromQueue:bool=True):# Pair and remove their entries from the queue
        
        #Create role
        #Create channel
        #Ping the new role or the users
        #Send a final DM to the group's dms
        print("user1 is {}".format(user1))
        user1obj = await self.bot.fetch_user(user1)
        user2obj = await self.bot.fetch_user(user2)
        await user1obj.send("You've been paired with {}!".format(user2obj.name))
        await user2obj.send("You've been paired with {}!".format(user1obj.name))
        
        print("[pair] users are into {}".format(interests))
        #Still need to make channel and role ties
        
        await self.giveWorkspace(user1,user2,interests) #Create role and channel
        
        if(removeFromQueue==True):
            kvRemoveKey(queuefile,user1)
            kvRemoveKey(queuefile,user2)
    
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
                interestsline = interests[0]+'.'
            elif(len(interests) > 1):
                for i, thing in enumerate(interests): #Iterate with an integer
                    if((i+1) == len(interests)): #Last entry
                        interestsline += " and {}.".format(thing)
                    elif((i+2) == len(interests)): #Second to last entry
                        interestsline += "{} ".format(thing)
                    else: #Anything else (3+ entries)
                        interestsline += "{}, ".format(thing)
        
        await channel.send("<@{}> and <@{}>, here's your private chatroom! You two were both interested in {}\nHave a conversation and say hi! When you're ready to set a goal for eachother, do **{}goal <goal>** and I'll help keep you two together for that goal.\nIf you want to unpair, use **{}abandon** to finish your conversation.\n".format(user1,user2,interestsline,bot_config.pfix,bot_config.pfix))
    
    
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

    @commands.command()
    async def li(self, ctx):
        """
        This lists all interests currently catalogued.
        """
        interests = kvGetKeys(interestsfile)
        #this kvGetKeys function comes from keyvaluemanagement.py. It treats a text file like a dictionary.
        
        interestlist = ""
        for interest in interests:
            interestlist += interest+'\n'
        ctx.send(interestlist);
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if (after.channel == None and before.channel.name.lower() != "yellbox"):
            await before.channel.delete()


def setup(bot):
    bot.add_cog(QueueCog(bot))
