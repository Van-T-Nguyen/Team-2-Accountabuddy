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

spread = spread()

lbIDFile = "leaderboardmessage.txt"

class leaderboard(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.homeserver = bot_config.Home_Server
        self.leaderboardMsg = None
        self.channel = self.bot.get_channel(826526139756969984)
        
        self.updateLeaderboard.start()
        
        
        

    def createLeaderboard(self):
        sortSheet(spread, "Leaderboard", 2, "DESCENDING")
        ids = []
        names = []
        scores = []
        ids, names, scores = get_sheet(spread, "Leaderboard")
        lb = "**Top Accountable Users:**\n"
        for i in range(len(scores)):
            lb += "**{}**: {}\t\t{}\n".format(i+1,names[i],scores[i]);
        #lb = "First: {}: {}\nSecond: {}: {}\nThird: {}: {}".format(names[0], scores[0], names[1], scores[1], names[2], scores[2])
        return lb

    @tasks.loop(seconds=30)
    async def updateLeaderboard(self):
        mid = 0
        msg = None
        #check file for leaderboard message
        with open(lbIDFile,"r") as f:
            
            try:
                mid = int(f.read())
                msg = await self.channel.fetch_message(mid)
            except Exception as e:
                print("[leaderboard updateLeaderboard] failed to read file or fetch message (ERROR IS OK): {}".format(e))
        
        #check if the message exists
        if(msg == None):
            #create new
            self.leaderboardMsg = await self.channel.send(self.createLeaderboard())
            
            with open(lbIDFile,"w") as f:
                f.write(str(self.leaderboardMsg.id))
            
        else:
            self.leaderboardMsg = msg
            await self.leaderboardMsg.edit(content=self.createLeaderboard())
        
        
        
        
        #if(self.leaderboardMsg == None):
        #    self.leaderboardMsg = await self.channel.send(self.createLeaderboard())
        #else:
        #    await self.leaderboardMsg.edit(content=self.createLeaderboard())

def setup(bot):
    bot.add_cog(leaderboard(bot))
