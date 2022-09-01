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

def load_user_data(filename:str):
    data = {}

    with open(filename, 'r') as f:
        for line in csv.DictReader(f):
            userid = line['UserID']
            points = line['Points']

            data[int(userid)] = int(points)

    return data


# test
# dict = {123:1, 234:2}
# save_user_data("testfile.csv", dict)
#
# test = load_user_data("testfile.csv")
# print(test)

###################
# server rank settings save/load
def save_rank_settings(filename: str, ranks: dict):
    fields = ['Points', 'Rank']
    with open(filename, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for key in ranks.keys():
            newDict = {'Points': key, 'Rank': ranks[key]}
            writer.writerow(newDict)

def load_rank_settings(filename: str, settings: dict):
    ranks = {}

    with open(filename, 'r') as f:
        for line in csv.DictReader(f):
            points = line['UserID']
            rank = line['rank']

            ranks[int(points)] = rank

    return ranks