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
import schedule
import time

@commands.command()
async def sendDaily(message, numDays, time):
	days = 1
	await message.channel.send("test message at {} for {} days".format(time, numDays))
	SCD = schedule.every().day.at(time).do(dailyMsg, message, days, numDays)

	while(days <= numDays):
		if SCD.should_run:
			days = days + 1
		await schedule.run_pending()
		await time.sleep(1)


async def dailyMsg(message, days, numDays):
	await message.channel.send("<@163824787540541441> test message. Day {} out of {}".format(days, numDays))
