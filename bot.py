import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
import discord.abc
import sys, traceback
import bot_config
import psutil
import os
import random

os.environ['DISPLAY'] = ':0' #linux req'd

textfiles = ['interests.txt','queue/userqueue.txt'] #Defining a text file here ensures it's existence when the bot runs. 

pfix = bot_config.pfix #Changeable prefix for calling the bot.

startup_extensions = ['blankcog','queueup'] #If you add a new module (python file) then add it's name here (without extension) and the bot will import it.

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

def removeFromList(path, key):
    with open(path, "r") as f:
        list = f.readlines()#.split("/n")
        list = [x.strip("\n") for x in list]

    with open(path, "w") as f:
        for x in list:
            if str(key) in x:
            elif str(key) not in x:
                f.write(x + "\n")
            else:
                pass

def isOnList(path,item,val):
    """Checks to see if this is on the list in the file."""
    f = open(path,"r")
    outlist = f.read().splitlines()
    f.close()
    i = 0;
    #print("{} in {}".format(str(item),outlist))
    for thing in outlist:
        i = i + 1;
        if( str(item) == thing):
            #print("{} is {}".format(str(item),thing))
            if(val):
                return i
            return True
    if(val):
        return -1
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
    await bot.change_presence(activity=discord.Game(name=(pfix+'help')))
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
    log_channel = bot.get_channel(bot_config.DM_Channel) #This channel ID logs DMs. Just for consistency.
    
    if isinstance(message.channel, discord.abc.PrivateChannel): #Forward DMs to a DM Logger channel.
        if message.author.id != 0: 
            #Sends message to the logs channel with the Name, ID, and message from the DM
            await log_channel.send(message.author.name + "/" + str(message.author.id) + " : " + message.content)
            if(message.attachments):
                a = ""
                for i in message.attachments: a += a + i.url
                
                await log_channel.send("Attachments: "+ a)
            
            if(pfix in message.content) or (bot.user in message.mentions): #Someone tried to execute a command in DMs.
                #Allow commands
                #await message.channel.send("Sorry, commands aren't supported in DMs.")
                #return
                pass
        #return
    
    await bot.process_commands(message)

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

bot.run(bot_config.token, reconnect=True)
