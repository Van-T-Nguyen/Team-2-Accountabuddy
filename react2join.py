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
goalsfile = "goals.txt"
leaderboardfile = "leaderboard.txt"
datadir = "queue/"
tiefile = datadir + "message2user.txt" #Ties a message ID with the associated user ID so it looks pretty.

queuefile = "queue/userqueue.txt" #Must be synchronized with queueup.py

textfiles = [tiefile] #Ensures these files exist on launch

joinemoji = "\U0001F4AC" # speech balloon, 💬



def processable_react(self,react,user):
        if(react.message.channel is not None): #Not in DMs
            if(user != self.bot.user): #Not us...
                return True;
        return False;

class ReactJoinCog(commands.Cog):
    '''Queue management'''

    def __init__(self, bot):
        self.bot = bot
        self.homeserver = bot_config.Home_Server
        self.queueCog = bot.get_cog("QueueCog") #hopefully?
        self.statchan = self.bot.get_channel(784133192944713770) #get-started in Acc. Univ.
        
        intents = discord.Intents.default()
        intents.reactions = True #Requires this intent for raw reaction add listener
        
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
    
    
    
    
    
    """
        
        Either every few minutes or on queue update, 
        update list:
            get queue
            get text file
            for each queue entry e:
                if text file has entry e == FALSE:
                    create new message and tie msg id to text file
        
        
        
    """
    
    
    
    async def listUpdate(self):
        """Updates the list to reflect the current queue."""
        
        self.queueCog = self.bot.get_cog("QueueCog") #hopefully?
        
        await self.statchan.trigger_typing()
        
        queueIDs, queueValues = get_sheet(spread(), "Queue") #[ userid, interests:str ]
        messageUIDs, messageObjIDs = kvGetKeysValues(tiefile) #[ userid, messageid ]
        
        #remove people not in queue
        
        print("queueIDs: {}\nmessageUIDs: {}".format(queueIDs,messageUIDs))
        for i in range(0,len(messageUIDs)):
            if(messageUIDs[i] not in queueIDs): #Message's user ID isn't in queue
                DeleteMe = await self.statchan.fetch_message(messageObjIDs[i]) #Message to delete
                kvRemoveKey(tiefile,messageUIDs[i])
                await DeleteMe.delete()#This can 404 if a message was deleted by hand.
                continue
        
        #Add people in queue but NOT present
        for i in range(0,len(queueIDs)):
            if(queueIDs[i] not in messageUIDs): #ID in queue doesn't have a message associated.
                #Create a message
                
                interests = []
                interests = (queueValues[i].split('$'))
                print("queueValues: {}".format(queueValues[i]))
                print("queueValues Split: {}".format(queueValues[i].split('$')))
                
                interestsline = "" #Format current interests given
                if(isinstance(interests,str)): #String, so just add.
                    interestsline = interests+" "
                else:
                    if(len(interests)==1):
                        try:
                            interestsline = interests[0]+'.'
                        except Exception as e:
                            interestsline = "."
                    elif(len(interests) > 1):
                        for j, thing in enumerate(interests): #Iterate with an integer
                            if((j+1) == len(interests)): #Last entry
                                interestsline += "and {}".format(thing)
                            elif((j+2) == len(interests)): #Second to last entry
                                interestsline += "{} ".format(thing)
                            else: #Anything else (3+ entries)
                                interestsline += "{}, ".format(thing)
                
                home = self.bot.get_guild(bot_config.Home_Server)
                username = int(queueIDs[i]) #Reolved to a mention
                message = await self.statchan.send("<@{}> - Interested in {}".format(username,interestsline))
                
                await message.add_reaction(joinemoji)
                
                
                
                kvAddValue(tiefile,queueIDs[i],message.id)
        
        #Get queue
        #Get text file
            #Add message if it's in the queue
            #Delete message if it's not
        
    
    #Listener for reacts
    #If react on a user, do checks and attempt queue then update the list.
    
    
    
    
    @commands.Cog.listener()
    #@commands.check(processable) #check doesn't work in events, only commands
    async def on_raw_reaction_add(self,payload):
        
        #This listener is different and will catch all reacts, even reacts that occurr on messages that aren't in the cache.
        #This is because messages can persist across bot restarts in this case. It uses a Payload object.
        
        
        if(payload.user_id == self.bot.user.id): #The bot made this react, ignore
            return print("[react2join] Bot made react, ignoring.")
        if(payload.guild_id is None):#None guild_ids are in DMs, ignore
            return print("[react2join] DM reaction, ignoring.")
        if(payload.event_type == "REACTION_REMOVE"):#Reaction removed, ignore.
            return print("[react2join] Reaction was removed, not added, ignoring.")
        if(payload.channel_id != self.statchan.id): #Not the list channel, ignore.
            return print("[react2join] Not in the list channel, ignoring.")
        validMessages = kvGetValues(tiefile) #All valid message IDs 
        if(str(payload.message_id) not in validMessages): #Not a message we can properly respond to, ignore
            return print("[react2join] Reaction added to a message I can't use, ignoring.")
        
        if(payload.emoji.name == joinemoji): #A request to join someone
            
            #user = await self.bot.fetch_member(payload.user_id)
            
            home = self.bot.get_guild(bot_config.Home_Server)
            user = await home.fetch_member(payload.user_id)
            
            #Return if they already have a buddy
            for x in user.roles:
                if x.name == "Accountabuds":
                    await user.send("You're already in a buddy pair, and I couldn't pair you to the person you selected.")
                    return
            
            #Get target user id from the tie list
            
            targetID = int(kvGetKey2(tiefile,str(payload.message_id))) #Works backwards to find the user ID associated with the message
            
            if(targetID == payload.user_id): #Can't join yourself!
                #await user.send("You can't join yourself!") #Silence is fine
                print("[react2join] Can't pair a user with themselves.")
                return
            
            interests = kvGetValue(queuefile,targetID) #gets interests of the target user, the only interest list we have
            interestslist = (interests.split('$'))
            
            self.queueCog = self.bot.get_cog("QueueCog") 
            await self.queueCog.pair(payload.user_id,targetID,interestslist) #Done
            
            #kvRemoveKey(tiefile,targetID) #REMOVAL IS DONE ELSEWHERE. Just remove from queue and gold.
            #await react.message.delete() #This is hard to do with a payload lookup. I'll let the list update do it.
            
            print("[react2join] pairing process complete")
            await self.listUpdate()
            
            
            #async def pair(self, user1: int, user2:int, interests:list = ['unknown'], removeFromQueue:bool=True)
        else:
            print("[react2join] incorrect emoji, ignoring.")

def setup(bot):
    bot.add_cog(ReactJoinCog(bot))
