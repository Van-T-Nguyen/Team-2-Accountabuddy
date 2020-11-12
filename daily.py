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

	@commands.command()
	async def daily(self, ctx, numDays):
		await ctx.send("Attempting to send messages every day")
		self.limit = int(numDays)
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
		await self.createMessage(self.ctx, self.day)
		#if self.day == self.limit:
		#	self.dailyMsg.stop()
		self.day = self.day + 1


	@commands.Cog.listener()
	async def on_guild_channel_create(self, channel):
		await channel.send("Hey all, AccountaBuddy here. As part of keeping you accountable:tm:, I'll be sending daily messages.")
		self.ctx = channel
		self.dailyMsg.start()

	async def createMessage(self, ctx, curDay):
		string = "AccountaBuddy checking in. How are you doing on your task? React if it is going well."
		dayCount = "It is day {}.".format(curDay)
		message = await ctx.send(string)
		await message.add_reaction('\U0001F44B')
		await ctx.send(dayCount)

	@commands.Cog.listener()
	async def on_reaction_add(self, react, user):
		numReact = react.count
		if (numReact > 2 and react.emoji ==  '\U0001F44B'):
			self.combo = self.combo + 1
			await self.comboMsg(self.ctx)

	async def comboMsg(self, ctx):
		await ctx.send("Thanks for checking in. Current score: {}".format(self.combo))

def setup(bot):
	bot.add_cog(sendDaily(bot))
