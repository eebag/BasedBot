import json
from datetime import date
import discord
from discord.ext import commands
import csv

# constants for discord bot stuff
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=';', intents=intents)

# Get the token for the server
token = None
tokenfile = "token.txt"
with open(tokenfile) as t:
    token = t.readline()

# Dicts for points and config
socialCredit = []
serverSettings = []
rankSettings = []  # ["rank": minimumsc, "rank": minimumsc, ... , "lowrank" : "lowrank"]


# this structure/similar one will allow for a rank that has no minimum sc (banished)
# hopefully also make it easy to find what rank requires what amount of sc

###########################################################
# Important/setup functions
def assignServerSettings(filename):
    global serverSettings
    with open(filename) as settings:
        serverSettings = json.load(settings)
        pass


async def setup(ctx):
    # Check current server and get id
    guild = ctx.guild
    id = guild.id

    # Load/make settings .json for server
    settingsfile = id + "-settings.json"  # guildid-settings.json
    # TODO: make sure file exists
    print("Opening settings from file: " + settingsfile + "\n for server " + guild.name)
    assignServerSettings(settingsfile)

    filename = guild.id + "-scores.csv"
    global SCFile
    SCFile = filename
    # TODO: make sure file exists
    loadSocialCredit(filename)
    ctx.send("Setup complete!")


# Load saved SC to dict, {name -> (current SC, gained today )}
def loadSocialCredit(filename):
    with open(filename, 'r') as data:
        for line in csv.DictReader(data):
            # print(type(line))
            userid = line['UserID']
            # print(userid)
            credit = line['Credit']
            # Credit is currently "(number ,number)"
            # want it in form "number number"
            credit = credit.replace(',', '')
            credit = credit.replace('(', '')
            credit = credit.replace(')', '')
            # print(credit)
            credit = tuple(map(int, credit.split(' ')))  # "number number" -> (int, int)
            # print(credit)
            # print(type(credit))
            dataDict = {userid: credit}
            socialCredit.append(dataDict)
    return


# Save social credit to given file
def saveSC():
    fields = ['UserID', 'Credit']
    with open(SCFile, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        print(type(socialCredit))
        writer.writeheader()
        for data in socialCredit:
            print(type(data))
            for id, credit in data.items():
                print(id, credit)
                newDict = {'UserID': id, 'Credit': credit}
                # print(type(newDict))
                writer.writerow(newDict)

    print("Done saving SC data")
    return


# TODO: reset all change values in current dict
def resetChange():
    saveSC()
    print("rest complete")
    pass


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
            return (member, True)

    return (None, False)


# Check users permissions
def userPermission(user):
    userid = user.id
    global serverSettings
    if (serverSettings["AdminRole"] in user.roles):
        return True
    else:
        return False


# sees if user has SC data
def doesDataExistFor(user):
    for data in socialCredit:
        if str(user.id) in data:
            return True
    return False


###########################################################
# Command functions

async def badCommand(ctx):
    await ctx.send("You just made a bad command.  I would subtract social credit from you if I could.")


# Initializes SC data for all members on server
async def initializeSC(ctx):
    i = 0
    guild = ctx.guild
    for member in guild.members:
        data = getSocialCreditData(member)
        if (member == bot) or member.bot:
            continue
        if not data:
            makeSCdata(member, 0)
            i += 1
        else:
            pass

    await ctx.send("Initialized data for " + str(i) + " users")


# Update users social credit
def updateSC(user, amount):
    if doesDataExistFor(user):
        changeSC(user, amount)
        return
    else:
        print("User not in data!")
        makeSCdata(user, amount)
        return -1


# updates existing dict entry
def changeSC(user, amount):
    # Getting global stuff
    global serverSettings
    # global rankSettings

    # Constants for use in function
    maxChange = serverSettings["MaxChange"]
    maxSC = serverSettings["MaxPoints"]
    minSC = serverSettings["MinPoints"]

    print("updating [" + user.name + "] social credit score by [" + str(amount) + "]")

    userid = str(user.id)
    data = getSocialCreditData(user)
    currentSCdata = data[userid]

    currentChange = currentSCdata[1]

    # if change exceeds max, add difference so max change is achieved
    if (currentChange + amount > maxChange):
        print("Exceeds max change!")
        newChange = (maxChange - currentChange)  # max change - current change = amount of change left
        if newChange == 0:  # early exit
            return
        print("adding [" + str(newChange) + "] to social credit instead")

        newSC = currentSCdata[0] + newChange

        if newSC > maxSC:
            newSC = maxSC
        elif newSC < minSC:
            newSC = minSC

        data[userid] = tuple((newSC, maxChange))
        return

    else:
        newSC = currentSCdata[0] + amount
        newChange = currentChange + amount

        if newSC > maxSC:
            newSC = maxSC
        elif newSC < minSC:
            newSC = minSC

        # update data
        data[userid] = tuple((newSC, newChange))
        saveSC()

    return


# Sets users points to given amount, ignores change
def setSCdata(user, amount):
    global serverSettings
    data = getSocialCreditData(user)
    currentData = data
    return


# adds new dict entry
def makeSCdata(user, amount):
    userid = str(user.id)
    new_values = {userid: (amount, amount)}
    socialCredit.append(new_values)
    saveSC()
    return


# returns dict for player if it exists
def getSocialCreditData(user):
    for data in socialCredit:
        if (str(user.id)) in data:
            return data
    return None


# Gets user social credit
def getSocialCredit(user):
    data = getSocialCreditData(user)
    if data:
        scData = data[str(user.id)]
        return scData[0]
    else:
        return None


# gets sc change
def getSocialCreditChange(user):
    data = getSocialCreditData(user)
    if data:
        scData = data[str(user.id)]
        return scData[1]
    else:
        return None


# TODO: assign a specific amount to user
def setSocailCredit(user, amount):
    pass


# Handles all social credit commands
@bot.command()
async def SocialCredit(ctx, *args):
    global lastDate
    if (date.today() != lastDate):
        print("Reseting change data")
        resetChange()
        lastDate = date.today()

    if len(args) == 0:
        await ctx.send("Social Credit commands: \n"
                       "add [user] [amount] -> adds [amount] social credit to [user]'s account\n"
                       "sub [user] [amount] -> subtracts [amount] from [user]'s social credit\n"
                       "[user] -> displays user's current social credit, and how much they've gained today")
    # add/subtract social credit
    elif len(args) == 3:

        # Make sure there are permissions
        if not userPermission((ctx.message.author)):
            await ctx.send("Nice try, pal.")
            return

        # check if arg 3 can become an int
        amount = args[2]

        try:
            amount = int(amount)
        except ValueError:
            print("NAN: " + amount)
            await badCommand(ctx)
            return

        # make it an integer
        amount = int(amount)

        # check if arg 2 is a user on the server
        target = args[1]
        user, _ = await findUser(target, ctx)

        # Make sure user was retrieved properly
        if not _:
            print("NOT A NAME")
            await badCommand(ctx)
            return

        # make sure user's data exists before trying to change it. if it doesn't exist, make it.
        if not (doesDataExistFor(user)):
            await ctx.send("User not in social credit database.... strange. Creating data for them.")
            makeSCdata(user, amount)
            await ctx.send("Users social credit data is now: \n"
                           + user.name + " with " + str(getSocialCredit(user)) + " social credit")
            return

        # add/subtract from social credit
        if (args[0] == "sub"):
            updateSC(user, -1 * amount)
            await ctx.send("Subtracting " + str(amount) + " social credit from " + user.name + "\n"
                                                                                               "New social credit is: " + str(
                getSocialCredit(user)))
        else:
            updateSC(user, amount)
            await ctx.send("Adding " + str(amount) + " social credit to " + user.name + "\n"
                                                                                        "New social credit is: " + str(
                getSocialCredit(user)))

    # Find user social credit, or save/load social credit
    elif len(args) == 1:
        target = args[0]

        # Check for save/load command
        if (target == "save"):
            print("Saving social credit")
            saveSC(SCFile)
            await ctx.send("Done saving social credit data")
            return
        elif (target == "load"):
            print("Loading social credit")
            loadSocialCredit(SCFile)
            await ctx.send("Done loading social credit data")
            return
        elif (target == "init"):  # initialize social credit data
            await ctx.send("Initializing social credit.  It has begun.")
            await initializeSC(ctx)
            # print(socialCredit)
            return

        user, _ = await findUser(target, ctx)

        if not _:
            print("NOT A NAME")
            await badCommand(ctx)
            return
        userSC = getSocialCredit(user)

        if userSC == None:
            await ctx.send("This person doesnt have any social credit data... suspicious")
            return

        gain = getSocialCreditChange(user)
        await ctx.send(
            "social credit for " + user.name + ": [" + str(userSC) + "], with [" + str(gain) + "] gained today!")
    else:
        await badCommand(ctx)
        print(args)


@bot.command()
async def consolePrint(ctx, args):
    await ctx.send("Printing args in console")
    print(args)


# Run the bot
@bot.event
async def on_ready():
    print("Loading Social Credit csv")
    loadSocialCredit(SCFile)
    print("Ready!")


bot.run(token)
