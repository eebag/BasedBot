# libraries that do kind things for me like make me not have to do code
import json
import discord
from discord import Member
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.utils import get
import math
import save_load_module
import os

# important stuff unrleated to discord api
GUILD = None # constant for holding the guild
STARTED = False

# constants for discord bot stuff
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=';', intents=intents)
bot.remove_command('help')

# current directory
CWD = os.getcwd()

# Get the token for the server
token = None
tokenfile = "token.txt"
with open(tokenfile) as t:
    token = t.readline()

# points credit dict {userid -> points}
memberPoints = {}
# roles dict {points -> role}
roles = {}

# top role and number of people who can attain it
toprole = None
topmembers = 0
toprequirement = 0

roleholders = []

# bottom role requiurements
bottomrole = None
bottomrequirement = 0

###########################################################
# Helper/Misc Functions

# Checks for data, returns true if found
# otherwise makes data and returns false
def check_for_data(user):
    userid = user.id
    global memberPoints
    if userid in memberPoints:
        print(f"{userid} already in dict. Value: {memberPoints[userid]}")
        return True
    else:
        print(f"adding {user.name} to dict")
        memberPoints[userid] = 0
        return False

#updates roles and top members
async def update_roles(ctx, user: discord.user,silent=False):
    global roles, memberPoints, toprole, topmembers, toprequirement, roleholders

    member = await discord.ext.commands.converter.MemberConverter().convert(ctx, str(user.id))

    if member == bot or member.bot:
        return

    userroles = member.roles
    userpoints = memberPoints[user.id]

    # check for normal roles
    roleamt = -math.inf
    newrole = None

    for amount in roles.keys():
        role = roles[amount]

        # make sure only top role is added
        if (userpoints >= amount) and (amount > roleamt):
            newrole = role
            roleamt = amount
        else:
            if role in member.roles:
                await member.remove_roles(role)

    # assign newrole
    if (not newrole in member.roles) and (newrole != None):
        print(f"adding {newrole} to {user.name}")
        await member.add_roles(newrole)
        if bottomrole in member.roles:
            await member.remove_roles(bottomrole)

    # remove all the roles that aren't newrole
    for r in roles.values():
        if r != newrole:
            await member.remove_roles(r)

    if userpoints < toprequirement and toprole in member.roles:
        await member.remove_roles(toprole)

    # check for top role
    if toprequirement > 0 and userpoints >= toprequirement and toprole != None:
        # print("Attempting to apply top role to user")
        # sort all members by points
        sorted_members = sorted(memberPoints.items(), key=lambda x: x[1], reverse=True)

        if topmembers > len(sorted_members):
            ctx.send("Error in updating top rank: More members allocated than have points")
        else:
            # print("a")
            for mem in roleholders:
                await mem.remove_roles(toprole)
            # print("b")
            for i in range(topmembers):
                tuserid = sorted_members[i][0]
                tmember = await discord.ext.commands.converter.MemberConverter().convert(ctx, str(tuserid))
                await tmember.add_roles(toprole)
                roleholders.append(member)
                print(f"{tmember} has attained {toprole}")

    # check for bottom role
    if userpoints <= bottomrequirement and bottomrole != None:
        await member.add_roles(bottomrole)

    if (userroles != member.roles) and (not silent):
        await ctx.send(f"{user.mention} has had their roles updated")

###########################################################
# Commands

# Admin help command
@bot.command()
@has_permissions(administrator=True)
async def commands(ctx, *args):
    if not STARTED:
        return

    if len(args) == 0:
        await ctx.send("Server point **ADMIN** commands: \n"
                       "```add      [user] [amount] -> adds [amount] point(s) to [user]'s account\n\n"
                       "remove   [user] [amount] -> subtracts [amount] from [user]'s points\n\n"
                       "setmaxrole [role] [num] [req] -> sets [role] as top role that only [num] people can hold, "
                       "with [req] as the minimum point requirement for attainment\n\n"
                       "setdefaultrole [role]    -> sets [role] as rank for 0 points\n\n"
                       "setbottomrole [role] [points] -> sets [role] as minimum role, below [amt] points\n\n"
                       "bankroll                 -> prints out EVERYONE'S points\n\n"
                       "update   [user]          -> updates user rank based on their points\n\n"
                       "updateall        [WIP]   -> updates EVERYONE'S rank based on their points (silent)```\n")


@bot.command(name="add")
@has_permissions(administrator=True)
async def add_points(ctx, amount: int, mention:str):
    if not STARTED:
        return

    global memberPoints

    #get user from mention
    userid = mention.replace("@","")
    userid = userid[1:][:len(userid) - 2]
    user = await bot.fetch_user(int(userid))

    if not user:
        print("No user")
        await ctx.send("Invalid user or self mention")
    elif user.bot:
        await ctx.send("Bots cant get points, bozo")
    else:
        check_for_data(user)
        memberPoints[user.id] = memberPoints[user.id] + amount
        await ctx.send(f"{user.mention} has been awarded {amount} points.  Congratulations!\n"
                       f"They now have {memberPoints[user.id]} points.")
        await update_roles(ctx, user)

@bot.command(name="remove")
@has_permissions(administrator=True)
async def remove_points(ctx, amount: int, mention:str):
    if not STARTED:
        return

    global memberPoints

    #get user from mention
    userid = mention.replace("@","")
    userid = userid[1:][:len(userid) - 2]
    user = await bot.fetch_user(int(userid))

    if not user:
        print("No user")
        await ctx.send("Invalid user or self mention")
    elif user.bot:
        await ctx.send("Bots cant get points, bozo")
    else:
        check_for_data(user)
        memberPoints[user.id] = memberPoints[user.id] - amount
        await ctx.send(f"{user.mention} has had {amount} points revoked. They now have {memberPoints[user.id]} points.")
        await update_roles(ctx, user)


@bot.command()
@has_permissions(administrator = True)
async def giverole(ctx, user : discord.Member, *, role : discord.role = None):
    if not STARTED:
        return

    if role in user.roles:
        await ctx.send(f"{user.mention} already has the role {role}!")
    else:
        await user.add_roles(role)
        await ctx.send(f"{role} added to {user.mention} !!")


@giverole.error
async def role_error(self, ctx, error):
    if not STARTED:
        return

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Nice try, pal")


@bot.command(name="setmaxrole")
@has_permissions(administrator = True)
async def set_max_role(ctx, name : str, amount : int = 1, requirement : int = 500):
    if not STARTED:
        return

    global toprole, topmembers, toprequirement

    rolename = name.replace("_", " ")
    role = get(GUILD.roles, name=rolename)
    if role is None:
        print("NO ROLE")
        await ctx.send("role does not exist")
    else:
        # role is being changed, remove it from existing top members
        if toprole != None:
            print(f"{toprole} BEING REPLACED WITH {role} AS TOP ROLE")
            global roleholders
            for member in roleholders:
                await member.remove_roles(toprole)

        toprole = role
        topmembers = amount
        toprequirement = requirement
        await ctx.send(f"{role} now set as max role, with {amount} people allowed to hold it")

@bot.command(name="setbottomrole")
@has_permissions(administrator = True)
async def set_botm_role(ctx, name :str, requirement : int = -250):
    if not STARTED:
        return

    global bottomrole, bottomrequirement
    rolename = name.replace("_", " ")
    role = get(GUILD.roles, name=rolename)

    if role is None:
        print("NO ROLE")
        await ctx.send("role does not exist")
    else:
        if bottomrole != None:
            print(f"{bottomrole} BEING REPLACED WITH {role} AS BOTTOM ROLE")
            for member in ctx.guild.members:
                if role in member.roles:
                    await member.remove_roles(bottomrole)

        bottomrole = role
        bottomrequirement = requirement

        await ctx.send(f"{role} now set as bottom role, with {requirement} points needed to attain it")

@bot.command(name ="setdefaultrole")
@has_permissions(administrator=True)
async def set_neutral_role(ctx, name: str):
    if not STARTED:
        return

    global roles

    rolename = name.replace("_", " ")
    role = get(GUILD.roles, name=rolename)
    if role is None:
        print("NO ROLE")
        await ctx.send("role does not exist")
    else:
        roles[0] = role
        print(f"{role} set for 0")
        await ctx.send(f"{role} now set 0 point role")

@bot.command(name="addrole")
@has_permissions(administrator = True)
async def add_role(ctx, name : str, amount : int):
    if not STARTED:
        return

    global roles
    rolename = name.replace("_", " ")
    role = get(GUILD.roles, name=rolename)

    if role is None:
        print("NO ROLE")
        print(name)
        print(GUILD.roles)
        await ctx.send("role does not exist")
    else:
        if amount:
            print(f"{role} adding for {amount}")
            roles[amount] = role
            await ctx.send(f"{role} added, achieved at {amount} points")

@bot.command(name="save")
@has_permissions(administrator=True)
async def save(ctx):
    if not STARTED:
        return

    global memberPoints, roles, toprole, toprequirement, topmembers

    filename = str(ctx.guild.id) + "-userdata.csv"
    save_load_module.save_user_data(filename, memberPoints)

    filename = str(ctx.guild.id) + "-ranksettings.csv"

    td = None
    bd = None
    if (toprole != None) and (topmembers > 0):
        td = [toprole, topmembers, toprequirement]

    if (bottomrole != None):
        bd = [bottomrole, bottomrequirement]
    save_load_module.save_rank_settings(filename, roles, td, bd)

@bot.command(name="load")
@has_permissions(administrator=True)
async def load(ctx):
    if not STARTED:
        return

    global memberPoints, roles

    filename = str(ctx.guild.id) + "-userdata.csv"
    memberPoints = save_load_module.load_user_data(filename)
    if memberPoints == -1:
        await ctx.send("There was no file or there was an error loading the file for user data")

    filename = str(ctx.guild.id) + "-ranksettings.csv"
    rdict = save_load_module.load_rank_settings(filename)
    if rdict == -1:
        await ctx.send("There was no file or there was an error loading the file for rank data")
    else: # convert into roles usable by discord.py
        for key in rdict.keys():
            if rdict[key].__contains__("%"):
                global toprole, toprequirement, topmembers
                toprequirement = key
                temp = rdict[key].split("%")
                temp[0] = temp[0].rstrip() # remove whitespace at end
                toprole = get(GUILD.roles, name = temp[0])
                topmembers = int(temp[1])
                print(f"{toprole} extracted as top role with {topmembers} members and minimum requirement of {toprequirement}")
            elif rdict[key].__contains__("&"):
                global bottomrole, bottomrequirement
                bottomrequirement = key
                temp = rdict[key].replace("&", "")
                bottomrole = get(GUILD.roles, name = temp)
                print(f"{bottomrole} extracted as bottom role with {bottomrequirement} as point requirement")
            else:
                roles[key] = get(GUILD.roles, name=rdict[key])

    for member in ctx.guild.members:
        await update_roles(ctx, member, True)
    await ctx.send("Done loading")

@bot.command(name="bankroll")
@has_permissions(administrator=True)
async def display_all_points(ctx):
    if not STARTED:
        return

    displaystr = "ALL members points: ```"
    for id in memberPoints:
        user = await bot.fetch_user(id)
        displaystr = displaystr + f"{user} has {memberPoints[id]} points\n"
    displaystr = displaystr + "```"
    await ctx.send(displaystr)

@bot.command(name="update")
@has_permissions(administrator=True)
async def update_user_rank_cmd(ctx, mention: str):

    userid = mention.replace("@","")
    userid = userid[1:][:len(userid) - 2]
    user = await bot.fetch_user(int(userid))
    if not user:
        await ctx.send("Invalid user")
        return
    await update_roles(ctx, user)

# non-admin commands
@bot.command(name="help")
async def help_command(ctx):
    if not STARTED:
        return

    await ctx.send("Server point commands:\n"
                       "```check                    -> prints out your current point balance\n"
                       "roles                    -> prints out all the roles and points needed to reach them\n"
                       "leaderboard [WIP]        -> prints out top (TBD) users and their points\n"
                       "pay [user] [amount]      -> pay a user with your points.  Implementation TBD```")

@bot.command(name="pay")
async def pay_user(ctx, mention:str, amount:int):
    userid = mention.replace("@","")
    userid = userid[1:][:len(userid) - 2]
    user = await bot.fetch_user(int(userid))

    if not user:
        await ctx.send("Invalid user")
        return

    balance = memberPoints[ctx.author.id]
    print(f"{ctx.author} has {balance} points and is trying to send {user} {amount} points")
    if (amount < 0) or (balance < amount):
        await ctx.send("Nice try, pal")
        return
    else:
        memberPoints[ctx.author.id] = balance - amount
        memberPoints[user.id] = memberPoints[user.id] + amount

    await update_roles(ctx, user)
    await update_roles(ctx, ctx.author)

@bot.command(name="check")
async def check_points(ctx):
    if not STARTED:
        return
    user = ctx.author
    check_for_data(user)
    print(memberPoints)
    amount = memberPoints[user.id]
    await ctx.send(f"{user.mention} you have {amount} points")

@bot.command(name="roles")
async def display_roles(ctx):
    global roles
    displaystring = "Roles determined by server points:\n```"

    if len(roles.keys()) == 0:
        displaystring = displaystring + "There are currently no roles attainable by regular point values\n"
    for key in roles.keys():
        displaystring = displaystring + "[" + str(key) + "] points -> " + str(roles[key]) + "\n"

    global toprole, topmembers, toprequirement, bottomrole, bottomrequirement

    # I know this is bad code. I just am too lazy to get to fixing it because i want to see this thing done right now
    tempstring = ""

    if (toprole == None) or (toprequirement == 0) or (topmembers == 0):
        tempstring = "There is currently no role for top ranked server members\n"
    else:
        tempstring = f"The highest role you can achieve is {toprole}, which only {topmembers} people can hold " \
                     f"and a minimum requirement of {toprequirement} points.\n"

    tempstring2 = ""
    if bottomrole == None:
        tempstring2 = "There is currently no role for members below a certain point value"
    else:
        tempstring2 = f"The lowest role you can achive is {bottomrole}, which is given to anyone with {bottomrequirement}" \
                      f" points or below."
    displaystring = displaystring + tempstring + tempstring2 + "```"

    await ctx.send(displaystring)

# Setup/initialization commands

# init: use when setting up bot for server.  Also usable as reset.
@bot.command()
@has_permissions(administrator=True)
async def init(ctx, *args):
    guild = ctx.guild
    i = 0
    for member in guild.members:
        if (member == bot) or member.bot:
            continue
        else:
            memberPoints[member.id] = 0
        i += 1
    await ctx.send("Initialized data for " + str(i) + " users")

# setup: use after bot restart
@bot.command()
@has_permissions(administrator=True)
async def start(ctx):
    global GUILD, STARTED
    GUILD = ctx.guild
    STARTED = True
    print("Bot started")

# Run the bot
@bot.event
async def on_ready():
    print("Ready!")

bot.run(token)
