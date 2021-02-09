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


class sendDaily(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.homeserver = bot_config.Home_Server
		self.day = 1
		self.limit = 0
		self.combo = 0
		self.ctx = None
		self.listOfChannels = []
		self.dailyMsg.start()

	@commands.command()
	async def daily(self, ctx):
		await ctx.send("Attempting to send messages every day")
		self.ctx = ctx
		self.day = 1
		self.dailyMsg.start()

    @commands.command()
    async def stop(self, ctx):
        self.ctx = ctx
        await self.ctx.send("Admin stop")
        self.dailyMsg.stop()

	@tasks.loop(minutes=1)
	async def dailyMsg(self):
		for channel in self.listOfChannels:
			await self.createMessage(channel)

	@commands.Cog.listener()
	async def on_guild_channel_create(self, channel):
		if(not isinstance(channel,discord.VoiceChannel)):"""
			self.day = 1
			self.combo = 0
			await channel.send("Hey all, AccountaBuddy here. As part of keeping you accountable:tm:, I'll be sending daily messages.")
			self.ctx = channel
			self.dailyMsg.start()"""
		print("About to add: ")
		print(channel)
		self.listOfChannels.append(channel)
		print(self.listOfChannels)



	@commands.Cog.listener()
	async def on_guild_channel_delete(self, channel):
		if(not isinstance(channel,discord.VoiceChannel)):
			print("About to delete: ")
			print(channel)
			self.listOfChannels.remove(channel)
			print(self.listOfChannels)

	async def createMessage(self, ctx):
		string = "AccountaBuddy checking in. How are you doing on your task?."
		#dayCount = "It is day {}.".format(curDay)
		message = await ctx.send(string)
		await message.add_reaction('\U0001F44B')
		#await ctx.send(dayCount)

    async def comboMsg(self, ctx):
        await ctx.send("Thanks for checking in. Current score: {}".format(self.combo))

def setup(bot):
    bot.add_cog(sendDaily(bot))
