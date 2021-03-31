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


class sendDaily(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.homeserver = bot_config.Home_Server
		self.ctx = None
		self.listOfChannels = []
		self.listOfUsers = []
		self.dailyMsg.start()

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

	@commands.command()
	async def leaderboard(self, ctx):
		sortSheet(spread, "Leaderboard", 2, "DESCENDING")
		ids = []
		names = []
		scores = []
		ids, names, scores = get_sheet(spread, "Leaderboard")
		await ctx.send("Leaderboard:")
		lb = "{}: {}\n{}: {}\n{}: {}".format(names[0], scores[0], names[1], scores[1], names[2], scores[2])
		await ctx.send(lb)

	@tasks.loop(minutes=1)
	async def dailyMsg(self):
		for channel in self.listOfChannels:
			await self.createMessage(channel)

	@commands.Cog.listener()
	async def on_guild_channel_create(self, channel):
		if(not isinstance(channel,discord.VoiceChannel)):
			print("About to add: ")
			print(channel)
			self.listOfChannels.append(channel)
			print(self.listOfChannels)



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

	async def createMessage(self, ctx):
		string = "AccountaBuddy checking in. How are you doing on your task?"
		message = await ctx.send(string)
		await message.add_reaction('\U0001F44B')

	@commands.Cog.listener()
	async def on_reaction_add(self, react, user):
		numReact = react.count
		if (numReact > 2 and react.emoji ==  '\U0001F44B'):
			await react.message.channel.send("Thanks for checking in. Your score has been incrased.")
			users = await react.users().flatten()
			print(users)
			for user in users:
				if(user.id != self.bot.user.id):
					rowNum = findValue(spread, "Leaderboard", str(user.id))
					if(rowNum != None):
						print("found")
						id = []
						names = []
						scores = []
						id, names, scores = get_sheet(spread, "Leaderboard")
						newScore = int(scores[rowNum]) + 1
						editValue(spread, "Leaderboard", str(user.id), 2, newScore)
					else:
						write_sheet(spread, "Leaderboard", [str(user.id), user.name, 1])


def setup(bot):
    bot.add_cog(sendDaily(bot))
