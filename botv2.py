#libraries that do kind things for me like make me not have to do code
import json
from datetime import date
import discord
from discord.ext import commands
import csv
import os

# constants for discord bot stuff
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=';', intents=intents)

#current directory
CWD = os.getcwd()

# Get the token for the server
token = None
tokenfile = "token.txt"
with open(tokenfile) as t:
    token = t.readline()

#Social credit dict {userid -> social credit}
socialCredit = {}


#Will handle all admin only commands
@bot.command
@commands.has_permissions(admin=True)
async def socialCredit(ctx, *args)
    pass


async def addSocialCredit(ctx, *args)
    pass

async def removeSocialCredit(ctx, *args)
    pass

#non-admin commands
@bot.command
async def checkSocialCredit(ctx, *args)
    pass

#Setup/initialization commands

#init: use when setting up bot for server.  Also usable as reset.
@bot.command
async def init(ctx, *args)
    pass

#setup: use after bot restart
@bot.command
async def setup(ctx, *args)
    pass

# Run the bot
@bot.event
async def on_ready():
    #print("Loading Social Credit csv")
    #loadSocialCredit(SCFile)
    print("Ready!")