import discord
from discord.ext import commands
import os
import asyncio
import queueup
import bot_config

from discord.ext.commands import has_permissions, MissingPermissions


#Changing the name of this class should also be reflected in the setup() function at the bottom of the code.
class BlankCog(commands.Cog):
    '''A blank placeholder cog for easy adding.'''

    def __init__(self, bot):
        self.bot = bot
        self.info = "This info can be modified anywhere and it retains it's value. It's like a global variable but better!"
        self.homeserver = bot_config.Home_Server
    @commands.command()
    #@commands.has_permissions(ban_members=True)
    async def test(self,ctx,*,argument:str = None):
        
        await ctx.send("Hi!")
        if(argument != None):
            await ctx.send("You sent me {}.".format(argument))
            
        await asyncio.sleep(5)
        
        await ctx.send("Also, 5 seconds passed.")

    @commands.command()
    async def test2(self,ctx):

        role = await queueup.QueueCog.makeRole(self, 162777143028350976)
        await queueup.QueueCog.makeRoom(self, 162777143028350976, role)
    
    """@commands.commands()
    async def clear(ctx):
        messages"""
        

def setup(bot):
    bot.add_cog(BlankCog(bot))
