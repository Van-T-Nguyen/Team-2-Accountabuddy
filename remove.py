import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
import discord.abc
import sys, traceback
import bot_config
import psutil
import os
import random
import re



async def remove_role(message, roleName):
	role = discord.utils.get(message.guild.roles, name=roleName)
	if role:
		await role.delete()
		await message.channel.send(roleName + ' has been deleted')
	else:
		await message.channel.send("Role was not found")

async def remove_channel(message, channelName):
	channel = discord.utils.get(message.guild.text_channels, name=channelName)
	if channel:
		await channel.delete()
		await message.channel.send(channelName + ' has been deleted')
	else:
		await message.channel.send("Channel was not found")
