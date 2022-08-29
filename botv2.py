# libraries that do kind things for me like make me not have to do code
import json
from datetime import date
import discord
from discord import Member
from discord.ext.commands import has_permissions
from discord.utils import get
from discord.ext import commands
import csv
import os

# constants for discord bot stuff
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=';', intents=intents)

# current directory
CWD = os.getcwd()

# Get the token for the server
token = None
tokenfile = "token.txt"
with open(tokenfile) as t:
    token = t.readline()

# Social credit dict {userid -> social credit}
socialCredit = {}
roles = ["1013907404460662786"]

###########################################################
# Helper/Misc Functions

# Finds to see if a user is in the server
async def findUser(target, ctx):
    guild = ctx.guild
    for member in guild.members:
        # print(member.name)
        if member.name == target:
            # print("Member found: " + member.name)
            # print(member.id)
            return member

    return False


# Admin help command
@bot.command()
async def commands(ctx, *args):
    if len(args) == 0:
        await ctx.send("Social Credit commands: \n"
                       "add [user] [amount] -> adds [amount] social credit to [user]'s account\n"
                       "sub [user] [amount] -> subtracts [amount] from [user]'s social credit\n"
                       "bankroll            -> prints out EVERYONE'S social score")
                       # "[user] -> displays user's current social credit, and how much they've gained today")


@bot.command(name="add")
async def add_social_credit(ctx, amount, user: discord.user = None):
    if not user:
        await ctx.send("Invalid user or self mention")
    else:
        await ctx.send(user.mention)


@bot.command()
@has_permissions(administrator = True)
async def giverole(ctx, user : discord.Member, *, role : discord.role = None):

    if role in user.roles:
        await ctx.send(f"{user.mention} already has the role {role}!")
    else:
        await user.add_roles(role)
        await ctx.send(f"{role} added to {user.mention} !!")


@giverole.error
async def role_error(self, ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Nice try, pal")


@bot.command(name="setmaxrole")
@has_permissions(administrator = True)
async def set_max_role(ctx, *, role : discord.role):
    await ctx.send(f"{role} now set as max role")


@bot.command(name="addrole")
@has_permissions(administrator = True)
async def add_role(ctx, *, role : discord.role):
    await ctx.send(f"{role} now added")


# non-admin commands
@bot.command(name="check")
async def check_social_credit(ctx, *args):
    pass


# Setup/initialization commands

# init: use when setting up bot for server.  Also usable as reset.
@bot.command()
async def init(ctx, *args):
    pass


# setup: use after bot restart
@bot.command()
async def setup(ctx, *args):
    pass


# Run the bot
@bot.event
async def on_ready():
    # print("Loading Social Credit csv")
    # loadSocialCredit(SCFile)
    print("Ready!")

bot.run(token)