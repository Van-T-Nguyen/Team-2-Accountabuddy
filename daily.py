import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
import discord.abc
import sys, traceback
import bot_config
import psutil
import os
import random
import re
import asyncio
from quickstart import *

import time
from keyvaluemanagement import *


spread = spread()

minTimeBetweenCheckins = 60*60*4 #12 hours
#minTimeBetweenCheckins = 60 #60 seconds
maxTimeBetweenCheckins = 60*60*72 #72 hours

datadir = "streakData/"

channelListPath = datadir+"watchchannels.txt"

dailyTimePath = datadir+"dailyTime.txt"
lastCheckedPath = datadir+"lastChecked.txt"
streakPath = datadir+"streak.txt"

textfiles = [dailyTimePath,lastCheckedPath,streakPath] #Make sure these files exist on boot

class sendDaily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.homeserver = bot_config.Home_Server
        self.ctx = None
        self.listOfChannels = []
        self.listOfChannelIDs = []
        self.listOfUsers = []
        self.dailyMsg.start()
        
        for entry in textfiles:
            try:
                f = open(entry,"r")
                f.close()
            except Exception as e:
                print("Making file: {}".format(entry))
                f = open(entry,"w")
                f.close()
        
        #self.dailyTime = {} #time when the last checkin occurred, defaults to 0
        #self.lastChecked = {} #channel:id, last user to initiate a checkin. 0 if no check in yet.
        #self.streak = {} #Streak points
        
        

    @commands.command()
    async def daily(self, ctx):
        await ctx.send("Attempting to send messages every day")
        self.dailyMsg.start()

    @commands.command()
    async def stop(self, ctx):
        await self.ctx.send("Admin stop")
        self.dailyMsg.stop()

    @commands.command()
    async def score(self, ctx):
        scoreRow = findValue(spread, "Leaderboard", str(ctx.author.id))
        if(scoreRow == None):
            await ctx.send("Sorry! You don't have a score. Join a group to start being accountable")
        else:
            ids = []
            names = []
            scores = []
            ids, names, scores = get_sheet(spread, "Leaderboard")
            score = scores[scoreRow]
            scoreText = "Your score is {}. ".format(score)
            await ctx.send(scoreText)

    #@commands.command()
    #async def leaderboard(self, ctx):
        #sortSheet(spread, "Leaderboard", 2, "DESCENDING")
        #ids = []
        #names = []
        #scores = []
        #ids, names, scores = get_sheet(spread, "Leaderboard")
        #await ctx.send("Leaderboard:")
        #lb = "{}: {}\n{}: {}\n{}: {}".format(names[0], scores[0], names[1], scores[1], names[2], scores[2])
        #await ctx.send(lb)

    @tasks.loop(minutes=1)
    async def dailyMsg(self):
        for channel in self.listOfChannels:
            #await self.createMessage(channel)
            pass

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if(not isinstance(channel,discord.VoiceChannel)):
            print("About to add: ")
            print(channel)
            self.listOfChannels.append(channel)
            self.listOfChannelIDs.append(channel.id)
            print(self.listOfChannels)
            
            #Initialize watch things
            
            
            
            kvSetValue(dailyTimePath,channel.id,0)
            kvSetValue(lastCheckedPath,channel.id,0)
            kvSetValue(streakPath,channel.id,0)
            
            #self.dailyTime[channel.id] = 0
            #self.lastChecked[channel.id] = 0
            #self.streak[channel.id] = 0



    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if(not isinstance(channel,discord.VoiceChannel)):
            print("About to delete: ")
            print(channel)
            try:
                self.listOfChannels.remove(channel)
            except Exception as e:
                print("exception {}".format(e))
            print(self.listOfChannels)
            
            
            kvRemoveKey(dailyTimePath,channel.id)
            kvRemoveKey(lastCheckedPath,channel.id)
            kvRemoveKey(streakPath,channel.id)
            
            

    async def createMessage(self, ctx):
        string = "AccountaBuddy checking in. How are you doing on your task?"
        message = await ctx.send(string)
        await message.add_reaction('\U0001F44B')

    @commands.Cog.listener()
    async def on_reaction_add(self, react, user):
        numReact = react.count
        if (numReact > 2 and react.emoji ==  '\U0001F44B'):
            await react.message.channel.send("Thanks for checking in, your scores have increased!")
            await react.message.clear_reaction('\U0001F44B')
            users = await react.users().flatten()
            print(users)
            for user in users:
                if(user.id != self.bot.user.id):
                    rowNum = findValue(spread, "Leaderboard", int(user.id)) - 2
                    if(rowNum != None):
                        print("found")
                        id = []
                        names = []
                        scores = []
                        id, names, scores = get_sheet(spread, "Leaderboard")
                        newScore = int(scores[rowNum]) + 1
                        editValue(spread, "Leaderboard", int(user.id), 2, newScore)
                    else:
                        write_sheet(spread, "Leaderboard", [str(user.id), user.name, 1])


    @commands.Cog.listener()
    async def on_message(self,message): #main listener thing
        #if message was in watched channel
            #if message wasn't bot
                ##checkin time check block
                #if(time.time() > lastChecked+minTimeBetweenCheckins):
                    #if(time.time() > maxTimeBetweenCheckins): #reset streak
                        #streak = 0
                    #if(lastChecked == 0):
                        #lastChecked = ctx.author.id #Half checked in, waiting for other user
                    #elif (lastChecked != ctx.author.id): #Fully checked in, start the streak
                        #streak +=1;
                        #dailyTime = time.time()
                        #lastChecked = 0;
                        #doDailyMessage()
                        
        pass
        
        
        channelIDList = kvGetKeys(dailyTimePath) #Returns a list of keys, in this case, channel IDs.
        
        if(str(message.channel.id) in channelIDList): #Watched channel
            #print("[daily on_message] watched channel")
            if(message.author.bot == False): #Not a bot
                #print("[daily on_message] not a bot")
                checktime = int(time.time())
                
                
                
                if(checktime > int(kvGetValue(dailyTimePath,message.channel.id))+maxTimeBetweenCheckins): #Reset streak, took too long
                    kvSetValue(streakPath,message.channel.id,0)
                    #self.streak[message.channel.id] = 0
                    #print("[daily onMessage] streak reset for channel {}".format(message.channel.id))
                    
                if(checktime > int(kvGetValue(dailyTimePath,message.channel.id)) + minTimeBetweenCheckins): #Past minimum time
                    
                    if(int(kvGetValue(lastCheckedPath,message.channel.id)) == 0): #Half checked in
                        #print("[daily on_message] Half check in performed")
                        #self.lastChecked[message.channel.id] = message.author.id
                        kvSetValue(lastCheckedPath,message.channel.id,message.author.id)
                        
                    elif (int(kvGetValue(lastCheckedPath,message.channel.id)) != message.author.id): #Fully checked in
                        #print("[daily on_message] Full check in performed")
                        await self.doCheckinMessage(message.channel,[int(kvGetValue(lastCheckedPath,message.channel.id)),message.author.id]) #The message channel, and the two users that checked in
                        #self.streak[message.channel.id] +=1
                        kvSetValue(streakPath,message.channel.id,int(kvGetValue(streakPath,message.channel.id))+1)
                        #self.dailyTime[message.channel.id] = checktime
                        kvSetValue(dailyTimePath,message.channel.id,checktime)
                        #self.lastChecked[message.channel.id] = 0
                        kvSetValue(lastCheckedPath,message.channel.id,0)
                    
    
    
    async def doCheckinMessage(self,channel, users:list):
        #Does the checkin message whenever a streak is increased.
        cid = channel.id
        
        streaktext = ""
        
        if(int(kvGetValue(streakPath,channel.id)) > 1):
            if(int(kvGetValue(streakPath,channel.id)) > 3):
                streaktext+=":fire::fire: " #flare
                
            streaktext += "Checked in {} times in a row!\n".format(int(kvGetValue(streakPath,channel.id)))
            
        
        output = "You both earned a chat point, keep it up!\n{}You can earn your next point in {} hours.\n".format(streaktext,int(minTimeBetweenCheckins/(60*60)))
        
        await channel.send(output)
        
        for userid in users:
            
            #user = #fetch user by id
            user = self.bot.get_user(userid)
            print("[doCheckinMessage] user found {}".format(user))
            
            if(user.id != self.bot.user.id):
                rowNum = findValue(spread, "Leaderboard", int(user.id))
                if(rowNum != None):
                    rowNum -= 2;
                    #print("found")
                    id = []
                    names = []
                    scores = []
                    id, names, scores = get_sheet(spread, "Leaderboard")
                    newScore = int(scores[rowNum]) + 1
                    editValue(spread, "Leaderboard", int(user.id), 2, newScore)
                else:
                    write_sheet(spread, "Leaderboard", [str(user.id), user.name, 1])
    
    



def setup(bot):
    bot.add_cog(sendDaily(bot))

