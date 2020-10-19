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
		self.ctx = None

	@commands.command()
	async def daily(self, ctx, numDays):
		await ctx.send("Attempting to send messages every day")
		self.limit = int(numDays)
		self.ctx = ctx
		self.day = 1

		self.dailyMsg.start()


	@tasks.loop(minutes=1)
	async def dailyMsg(self):
		await self.createMessage(self.ctx, self.day, self.limit)
		if self.day == self.limit:
			self.dailyMsg.stop()
		self.day = self.day + 1



	async def createMessage(self, ctx, curDay, maxDay):
		string = "Hey all, AccountaBuddy here. I'm here to check in on how you are doing in your tasks."
		dayCount = "It is day {} out of {}.".format(curDay, maxDay)
		await ctx.send(string)
		await ctx.send(dayCount)

def setup(bot):
	bot.add_cog(sendDaily(bot))
