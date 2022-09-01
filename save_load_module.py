import csv
import discord
from discord import Member
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.utils import get
import csv

###################
# module for saving and loading information


# CSV/Userdata save/load
def save_user_data(filename:str, data:dict):
    fields = ['UserID', 'Points']
    with open(filename, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for key in data.keys():
            newDict = {'UserID': key, 'Points': data[key]}
            writer.writerow(newDict)
    pass

def load_user_data(filename:str):
    pass


# test
dict = {123:1, 234:2}
save_user_data("testfile.csv", dict)