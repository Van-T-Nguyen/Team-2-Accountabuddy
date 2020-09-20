import discord
from discord.ext import commands
import os
import asyncio
from discord.ext.commands import has_permissions, MissingPermissions
import bot_config
from keyvaluemanagement import *
from filemanagement import *



interestsfile = "interests.txt"
datadir = "queue/"
queuefile = datadir+"userqueue.txt"


#Changing the name of this class should also be reflected in the setup() function at the bottom of the code.
class QueueCog(commands.Cog):
    '''Queue management'''

    def __init__(self, bot):
        self.bot = bot
        self.homeserver = bot_config.Home_Server
    
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
    
    @commands.command()
    async def join(self,ctx):
        """Initiate joining of the queue."""
        
        #Check if in the home server
        #if not...
        #...Invite and bail.
        if(await self.userInServer(ctx.author.id,self.homeserver) == False): #Not in home server.
            #Invite to server
            await ctx.send("You're not in my home server, so you'll have to join it first before I can include you.\n Here you go: {}".format(bot_config.Invite_To_Home_Server))
            return #Abort
        
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
                    await ctx.send("I couldn't follow you at all... Try again later, mayhaps?")
                    return
                continue
            else:
                break
            
            
        
        if(tries==0)
        
        debugtext = "Parsed interests: {}\n".format(readinterests)
        
        debugtext += "Relations:\n"
        for read in readinterests:
            debugtext += "{}: {}\n".format(read,kvGetValue(interestsfile,read).split("$"))
        
        await ctx.send(content=debugtext)
        
        
        return
        
        
        
        #Ask for interests
        #Include in queue
        #Run Queue update
        
        pass
    
    async def removeFromQueue(self,userid:int):
        """Removes a user from the queue."""
        pass
    
    async def addToQueue(self,userid:int,interests:list):
        """Add a user to the queue with these interests."""
        
        
        pass
    
    @tasks.loop(seconds=60.0) #This runs every minute.
    async def queueUpdate(self):
        """Check for pairs and pair them if applicable."""
        #Check for possible pairings in the file.
        #If a pair is found, run pair() from another Cog and remove them from the queue list. They should now be paired!
        
        pass
    
    #Creates a new role and assigns it to an Accountabuddy pair
    
    async def makeRole(self, user1: int):#, user2: int):
        guild = bot_config.Home_Server
        home = self.bot.get_guild(guild)
        role = await home.create_role(name = "Accountabud", color = discord.Color(0x0000ff))
        await home.get_member(user1).add_roles(role)
        #await home.get_member(user2).add_roles(role)
        return role

    #Creates a text channel only users with a certain role can access
    async def makeRoom(self, userid: int, roleid: int):
        guild = bot_config.Home_Server
        home = self.bot.get_guild(guild)
        role = home.get_role(roleid)
        category = discord.utils.get(home.categories, name="pairs")
        default = home.default_role
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = True
        overwrite.read_messages = True
        channel = await category.create_text_channel('meeting room')
        await home.get_channel(channel).edit(sync_permissions=False)
        await home.get_channel(channel).set_permissions(role, read_messages=True, send_messages=True)
        await home.get_channel(channel).set_permissions(default, read_messages=False, send_messages=False)

    """async def deleteRole(self):
        guild = bot_config.Home_Server
        home = self.bot.get_guild(guild)
        await home.delete_role(name="Accountabud")"""

    def setup(self, bot):
        bot.add_cog(QueueCog(bot))
