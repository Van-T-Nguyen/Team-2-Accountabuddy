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
import time

spread = spread()
interestsfile = "interests.txt"
datadir = "queue/"
#tiefile = datadir + "message2user.txt" #Ties a message ID with the associated user ID so it looks pretty.



#textfiles = [tiefile] #Ensures these files exist on launch

queueemoji = "\U00002705" # checkmark, ✅





def processable_react(self,react,user):
        if(react.message.channel is not None): #Not in DMs
            if(user != self.bot.user): #Not us...
                return True;
        return False;

class ReactInterestCog(commands.Cog):
    '''Queue management'''

    def __init__(self, bot):
        self.bot = bot
        self.homeserver = bot_config.Home_Server
        self.queueCog = bot.get_cog("QueueCog") #hopefully?
        #self.statchan = self.bot.get_channel(784133192944713770) #seeking-buddy in Acc. Univ.
        self.intchan = self.bot.get_channel(807132758265561169) #get-started in Acc. Univ.
        self.updatetime = -1 #Above 1 means update when this time is equal to time.time()
        
        self.translationbuffer = {} #Filled on boot.
        self.OKmessages = [] #Message IDs that are mine and also in self.intchan.
        
        self.updateids = [] #All IDs that made a reaction, and thus need to be updated in the database.
        
        intents = discord.Intents.default()
        intents.reactions = True #Requires this intent for raw reaction add listener
        
        
        """
        for entry in textfiles:
            try:
                f = open(entry,"r")
                f.close()
            except Exception as e:
                print("Making file: {}".format(entry))
                f = open(entry,"w")
                f.close()
        """

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
    
    
    
    
    
    """
        
        Either every few minutes or on queue update, 
        update list:
            get queue
            get text file
            for each queue entry e:
                if text file has entry e == FALSE:
                    create new message and tie msg id to text file
        
        
        
    """
    
        
    
    async def listInit(self):
        """Updates the list to reflect the current interest options."""
        #SHOULD ONLY RUN ON STARTUP.
        
        self.queueCog = self.bot.get_cog("QueueCog") #hopefully?
        await self.intchan.trigger_typing()
        
        #Get list of interests
        interests = kvGetKeys(interestsfile)
        
        #Get list of messages
        messages = await self.intchan.history(limit=200).flatten()
        
        
        #Compare
        ##For each message:
        ##If on interst list, delete the interest so it isn't made later.
        ## Add it to the internal messageID-to-interest buffer.
        ##If NOT on interest list, delete the message.
        
        for m in messages:
            if(m.author.id == self.bot.user.id): #A message from our bot
                if(m.content in interests): #Lines up with an existing interest
                    interests.remove(m.content) #Remove from interest list so we don't recreate it later
                    await asyncio.sleep(0.1)
                    self.translationbuffer[m.id] = m.content #Add to our translation buffer
                    self.OKmessages.append(m.id)
                    print("[react2interest listinit] Recognizing message {}".format(m.content))
                    continue
                else:
                    print("[react2interest listinit] Erasing unnecessary message {}".format(m.content))
                    await m.delete()
        
        #for each interest:
        ##create a corresponding message.
        ## Add it to the internal messageID-to-interest buffer.
        
        for i in interests:
            print("[react2interest listinit] Creating message {}".format(i))
            m = await self.intchan.send(i)
            await m.add_reaction(queueemoji)
            self.translationbuffer[m.id]=i
            self.OKmessages.append(m.id)
            await asyncio.sleep(0.75)
        
        #Everything should be ready at this point.
        
        print("[react2interest listinit] Updating queue from react counts...")
        await self.listUpdate() #Update now... just to be sure.
        
    
    
    
    async def listUpdate(self):
        """Check the current interest list and it's reacts, then submit those users to the queue."""
        
        messages = await self.intchan.history(limit=200).flatten()
        queueout = {} #Outgoing queue list once finished.{userid:"Interest1$Interest2")
        blacklist = [] #Blacklisted ids that are already paired.
        whitelist = [] #Whitelisted ids that are verified NOT to be paired.
        home = self.bot.get_guild(bot_config.Home_Server)
        
        print("[react2interest listUpdate] Querying reactions in interest channel")
        
        async def addinterest(userid:int,interest:str): #Adds a user:interest pair to our temporary databse, to push off to the main one.
            if(userid in blacklist):
                return #Do nothing if we're blacklisting this peep.
            if(userid not in whitelist):
                #Check to see if they're paired.
                
                user = await home.fetch_member(userid)
                for x in user.roles:
                    if x.name == "Accountabuds": 
                        print("[react2interest listUpdate] Ignoring already paired user")
                        blacklist.append(userid)
                        continue #Ignore if this user is already queued.
                whitelist.append(userid) #Whitelist them if they made it through.
                
            if(userid in queueout): #Key exists, appending a second or more interest onto someone's existing one.
                queueout[userid] = queueout[userid]+"${}".format(interest)
            else:#Key doesn't exist, adding an interest where someone didn't have one before.
                queueout[userid] = interest
        
        
        for m in messages:
            if(m.author.id == self.bot.user.id): #My message
                #Fetch current reactions to it
                reacts = m.reactions
                for r in reacts: #All reactions on a message
                    if(r.emoji == queueemoji): #Emoji match, so search through these. Below is everyone that checked the checkmark.
                        reactors = await r.users().flatten() #Everyone who checked the checkmark.
                        for r2 in reactors:
                            if(r2.id != self.bot.user.id): #Not us, don't queue ourselves!
                                print("[react2interest listupdate] {} reacted to {}".format(r2.id,m.content))
                                await addinterest(r2.id,m.content) #Add this user's ID to the dictionary, along with the content of the message (the interest)
        
        #At this point, queueout is a dictionary with user IDs, each id having a string of every interest they're interested in.
        
        #Get the list of the current queue entrants and either overwrite their entries or supplement them.
        
        
        
        
        #Get interest. Find user a user? Delete it.
        
        #queuefile
        ignorethisID = [] #IDs that don't need to be scrubbed from the database OR re-added.
        
        ids, goals = get_sheet(spread,"Queue")
        
        #print("[react2interest listUpdate] QUEUEOUT: {}".format(queueout))
        #Push our temporary database to the main database.
        print("[react2interest listUpdate] Pushing changes to main database")
        
        for outid in queueout:
            outinterests = queueout[outid]
            if(ids is not None): #List isn't empty
                if(str(outid) in ids): #Key already exists
                    #pass #No error... yet.
                    #print("CHECK {} == {}".format(goals[ids.index(str(outid))],outinterests))
                    if(goals[ids.index(str(outid))] == outinterests 
                       and outid not in ignorethisID
                       and outid not in blacklist): #If databse goal entry is equivalent to our found one, ignore it.
                        ignorethisID.append(outid)
                        print("[react2interest listupdate] Ignoring {} because their entry in the database is already ok.".format(outid))
                        continue
                    deleteEntry(spread,"Queue",outid) #No actually there is an error, if need be.
                    print("[react2interest listUpdate] Deleting entry {} to make space for newer value.".format(outid))
                
            if(outid not in ignorethisID): #If not already satisfied
                if(outid not in blacklist): #Or blacklisted
                    write_sheet(spread, "Queue", [str(outid), outinterests]) #Out we go
                    print("[react2interest listUpdate] Writing in sheet: {}/{}".format(outid,outinterests))
                else:
                    print("[react2interest listUpdate] Writing in sheet failed because this user was blacklisted.")
        
        
        
        #If a user is in the Database, but ISN'T in our local copy, check to see if they're on self.updateids. If they are, our DB overwrites them, and we safely remove them.
        print("[react2interest listUpdate] Checking for people from external DB with no checked interests.")
        #await asyncio.sleep(3)
        ids, goals = get_sheet(spread,"Queue")
        
        if(ids is None): ids = []
        if(goals is None): goals = []
        
        internalids = [] ; 
        for i in queueout:
            internalids.append(i) # Make list of every ID in our internal database for quick comparisons.
        
        for dbid in ids: #For each id in the online database
            #Do they exist in the net db, while not existing in our local db?
            #print("[react2interest listUpdate] is {} in {}?".format(dbid,internalids))
            if( int(dbid) not in internalids):
                #print("[react2interest listUpdate] ID {} Not in internal database".format(dbid))
                #If not, did they interact with our checkmarks?
                if(int(dbid) in self.updateids): 
                    #Our entry overrides.
                    print("[react2interest listupdate] {} interacted with checkmarks and now has no interests. Removing from DB.".format(dbid))
                    deleteEntry(spread,"Queue",int(dbid))
                else:
                    print("[react2interest listUpdate] Not removing entry {} because they haven't interacted with a checkmark- possibly present in database from other means?")
        
        #Update the list and finished.
        self.updateids = [] #Clear our cache of update users
        self.queueCog = self.bot.get_cog("QueueCog") #hopefully.
        await self.queueCog.queueUpdate() #Checks for possible pairs and handles them.
        #await self.queueCog.queueUpdate() #Do it twice because I can't call for a react2join list update on it's own.
        
    
    #Listener for reacts
    @commands.Cog.listener()
    #@commands.check(processable) #check doesn't work in events, only commands
    async def on_raw_reaction_add(self,payload):
        
        #This listener is different and will catch all reacts, even reacts that occurr on messages that aren't in the cache.
        #This is because messages can persist across bot restarts in this case. It uses a Payload object.
        if(payload.user_id not in self.updateids):
            self.updateids.append(payload.user_id)
            
        
        if(payload.user_id == self.bot.user.id): #The bot made this react, ignore
            return print("[react2interest] Bot made react, ignoring.")
        if(payload.guild_id is None):#None guild_ids are in DMs, ignore
            return print("[react2interest] DM reaction, ignoring.")
        #if(payload.event_type == "REACTION_REMOVE"):#Reaction removed, ignore. ##ALLOW: Removing reactions is grounds for an update.
            #return print("[react2interest] Reaction was removed, not added, ignoring.")
        if(payload.channel_id != self.intchan.id): #Not the list channel, ignore.
            return print("[react2interest] Not in the list channel, ignoring.")
        if(payload.message_id not in self.OKmessages): #Not a message we can properly respond to, ignore
            return print("[react2interest] Reaction added to a message I can't use, ignoring.")
        if(str(payload.emoji) != queueemoji):
            return print("[react2interest] Reaction isn't queueemoji, ignoring.")
        print("[react2interest] Updating emoji detected, waiting 5 seconds...")
        self.updatetime = time.time() #+ 5
    
    @commands.Cog.listener()
    #@commands.check(processable) #check doesn't work in events, only commands
    async def on_raw_reaction_remove(self,payload):
        
        #This listener is different and will catch all reacts, even reacts that occurr on messages that aren't in the cache.
        #This is because messages can persist across bot restarts in this case. It uses a Payload object.
        if(payload.user_id not in self.updateids):
            self.updateids.append(payload.user_id)
        
        if(payload.user_id == self.bot.user.id): #The bot made this react, ignore
            return print("[react2interest] Bot made react, ignoring.")
        if(payload.guild_id is None):#None guild_ids are in DMs, ignore
            return print("[react2interest] DM reaction, ignoring.")
        #if(payload.event_type == "REACTION_REMOVE"):#Reaction removed, ignore. ##ALLOW: Removing reactions is grounds for an update.
            #return print("[react2interest] Reaction was removed, not added, ignoring.")
        if(payload.channel_id != self.intchan.id): #Not the list channel, ignore.
            return print("[react2interest] Not in the list channel, ignoring.")
        if(payload.message_id not in self.OKmessages): #Not a message we can properly respond to, ignore
            return print("[react2interest] Reaction added to a message I can't use, ignoring.")
        if(str(payload.emoji) != queueemoji):
            return print("[react2interest] Reaction isn't queueemoji, ignoring.")
        
        print("[react2interest] Updating emoji detected, waiting 5 seconds...")
        self.updatetime = time.time() #+ 5
    
def setup(bot):
    bot.add_cog(ReactInterestCog(bot))
    bot.loop.create_task(addinterestservice(bot))


async def addinterestservice(bot):
    Cog = bot.get_cog('ReactInterestCog')
    print("[react2interest] Performing setup...")
    await Cog.listInit() #Fills the translation buffer and creates messages
    print("[react2interest] Done.")
    busy = False
    while True:
        #hello
        
        if(Cog.updatetime != -1):
            if(time.time() > Cog.updatetime):
                while(busy==True):
                    await asyncio.sleep(1)
                Cog.updatetime = -1
                busy = True
                await Cog.listUpdate()
                busy = False
        await asyncio.sleep(1)
        









    
    
    
    
    
    
    
    
    
    
    
    

    

    

    
    
    
