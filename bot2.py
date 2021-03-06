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
import schedule
import time
from remove import remove_role, remove_channel

os.environ['DISPLAY'] = ':0' #linux req'd

textfiles = ['interests.txt'] #Defining a text file here ensures it's existence when the bot runs. 

pfix = '/' #Changeable prefix for calling the bot.

startup_extensions = ['blankcog','queueup', 'daily'] #If you add a new module (python file) then add it's name here (without extension) and the bot will import it.

def makeList(path):
    """Return a list of ints from this file."""
    f = open(path,"r")
    outlist = f.read().splitlines()
    f.close()
    return outlist

def addToList(path,item):
    """Adds item to path. Does not check if it's already present."""
    f = open(path,"a")
    f.write(str(item)+"\n")
    f.close()

def removeFromList(path, item):
    with open(path, "r") as f:
        list = f.readlines()#.split("/n")
        list = [x.strip("\n") for x in list]

    with open(path, "w") as f:
        for x in list:
            if x != str(item):
                f.write(x + "\n")
            elif x == list[(len(list)-1)] and list[(len(list)-1)] != "\n":
                f.write("\n")
            else:
                pass

def isOnList(path,item):
    """Checks to see if this is on the list in the file."""
    f = open(path,"r")
    outlist = f.read().splitlines()
    f.close()
    #print("{} in {}".format(str(item),outlist))
    for thing in outlist:
        if( str(item) == thing):
            #print("{} is {}".format(str(item),thing))
            return True
    
    return False

def get_prefix(bot, msg):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""
    prefixes = [pfix]
    # Check to see if we are outside of a guild. e.g DM's etc.
    if msg.channel is None:
        return ''
    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, msg)

desc = '''AccountaBuddy'''

bot = commands.Bot(command_prefix=get_prefix,description=desc)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    #bot.remove_command('help')
    if __name__ == '__main__':
        for extension in startup_extensions:
            try:
                bot.load_extension(extension)
            except Exception as e:
                print('Failed to load extension ' + extension, file=sys.stderr)
                traceback.print_exc()
    
    for entry in textfiles:
        try:
            f = open(entry,"r")
            f.close()
        except Exception as e:
            print("Making file: {}".format(entry))
            f = open(entry,"w")
            f.close()
    print('Successfully logged in and booted!')


@bot.event
async def on_message(message):
	if(message.author != bot.user):
		check = re.search("\/test", message.content)
		pattern_remove = re.compile("/remove (\S+)")
		remove_check = pattern_remove.match(message.content)
		pattern_challen = re.compile("/removeChannel (\S+)")
		channel_check = pattern_challen.match(message.content)
		test = message.content.split()

		if(remove_check):
			await message.channel.send("Attempting to remove: " + remove_check.group(1))
			await remove_role(message, remove_check.group(1))
		if(channel_check):
			await message.channel.send("Attempting to remove: " + channel_check.group(1))
			await remove_channel(message, channel_check.group(1))
		if(check):
			 await message.channel.send("Test complete. Congradulations")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found- try "+pfix+"help!")
    raise error

"""
@commands.command()
@commands.check(is_super)
async def keylock(ctx):
    if keylocked == False: #enable
        keylocked = True
        await ctx.send("Keylock enabled - Superusers only!")
    else:
        keylocked = False
        await ctx.send("Keylock disabled - Everyone can play!")
        
"""

#--------------------------------------------------------------------------------------------------------


bot.run(bot_config.token, reconnect=True)
