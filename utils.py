import csv
import os
from definitions import *
import ntplib
import datetime
import discord
from discord.ext import tasks

intents = discord.Intents.default()
intents.members = True
CLIENT = discord.Client(intents=intents)

def Check_channel(channel_id):
    for id in LISTENED_CHANNEL_IDS:
        if channel_id == id:
            return True
    return False

def Safe_delete_file(filename):
    if os.path.isfile(filename):
        os.remove(filename)
    #     return True
    # return False

async def sort_and_display_top5():
    Date = datetime.datetime.utcnow()
    i = 0
    l = []
    x = 0
    Channel = CLIENT.get_channel(854601844905738260)
    for key in DAILY_DICT:
        l.append((key, DAILY_DICT[key]['upvote']))
    l.sort(reverse=True, key=lambda tup: tup[1])
    length = len(l)
    embed = discord.Embed(
        title="Top 5 daily user submited suggestions:"
    )
    while x < length and length > 0 and i < 5:
        if not DAILY_DICT[l[x][0]]['message']:
            x += 1
        else:
            embed.add_field(name=DAILY_DICT[l[x][0]]['author'], value=DAILY_DICT[l[x][0]]['message'], inline=True)
            embed.add_field(name="Suggestion has:", value='{}{} upvotes and {}{} downvotes'.format(DAILY_DICT[l[x][0]]['upvote'],
                                                                                CLIENT.get_emoji(881643747325124678),
                                                                                DAILY_DICT[l[x][0]]['downvote'],
                                                                                CLIENT.get_emoji(881644076661870623)),
                            inline=True)
            embed.add_field(name="\n\u200b", value="\n\u200b", inline=True)
            embed.set_footer(text=Date.strftime("%b %d, %Y"))
            i += 1
            x += 1
    if i > 0:
        await Channel.send(embed=embed)
        Channel = CLIENT.get_channel(852835966992908292)
        await Channel.send(embed=embed)
    else:
        pass
        #print("Bot has no suggestions to display")
    # clear
    DAILY_DICT.clear()
    Safe_delete_file(DAILY_CSV)

async def sort_and_display_top10():
    Date = datetime.datetime.utcnow()
    i = 0
    l = []
    x = 0
    Channel = CLIENT.get_channel(854601844905738260)
    for key in WEEKLY_DICT:
        l.append((key, WEEKLY_DICT[key]['upvote']))
    l.sort(reverse=True, key=lambda tup: tup[1])
    length = len(l)
    embed = discord.Embed(
        title="Top 10 weekly user submited suggestions:"
    )
    while x < length and length > 0 and i < 5:
        if not WEEKLY_DICT[l[x][0]]['message']:
            x += 1
        else:
            embed.add_field(name="User: {}".format(WEEKLY_DICT[l[x][0]]['author']),
                            value=WEEKLY_DICT[l[x][0]]['message'], inline=True)
            embed.add_field(name="Suggestion has:", value='{}{} upvotes and {}{} downvotes'.format(WEEKLY_DICT[l[x][0]]['upvote'],CLIENT.get_emoji(881643747325124678),WEEKLY_DICT[l[x][0]]['downvote'],CLIENT.get_emoji(881644076661870623)),
                            inline=True)
            embed.add_field(name="\n\u200b", value="\n\u200b", inline=True)
            i += 1
            x += 1
    embed1 = discord.Embed()
    while x < length and length > 0 and i < 10:
        if not WEEKLY_DICT[l[x][0]]['message']:
            x += 1
        else:
            embed1.add_field(name="User: {}".format(WEEKLY_DICT[l[x][0]]['author']),
                             value=WEEKLY_DICT[l[x][0]]['message'], inline=True)
            embed1.add_field(name="Suggestion has:", value='{}{} upvotes and {}{} downvotes'.format(WEEKLY_DICT[l[x][0]]['upvote'],
                                                                                CLIENT.get_emoji(881643747325124678),
                                                                                WEEKLY_DICT[l[x][0]]['downvote'],
                                                                                CLIENT.get_emoji(881644076661870623)),
                             inline=True)
            embed1.add_field(name="\n\u200b", value="\n\u200b", inline=True)
            embed1.set_footer(text=Date.strftime("%b %d, %Y"))
            i += 1
            x += 1
    if i > 0:
        await Channel.send(embed=embed)
        Channel = CLIENT.get_channel(852835966992908292)
        await Channel.send(embed=embed)
    if i > 5:
        await Channel.send(embed=embed1)
        Channel = CLIENT.get_channel(852835966992908292)
        await Channel.send(embed=embed1)
    else:
        pass
        #print("Bot has no suggestions to display")
    # clear
    WEEKLY_DICT.clear()
    Safe_delete_file(WEEKLY_CSV)

def Get_UTC_time():
    try:
        time = ntplib.NTPClient().request('uk.pool.ntp.org', version=3).tx_time
        return datetime.datetime.utcfromtimestamp(time)
    except:
        time = datetime.datetime.utcnow()
        return time


def Check_time(time):
    if Get_UTC_time().strftime('%H:%M:%S') == time:
        return True
    return False

def Check_week_day(day):
    if Get_UTC_time().strftime('%a') == day:
        return True
    return False

@tasks.loop(seconds=0.9)
async def Print_top_suggestions():
    if Check_time('20:00:00'):
        await sort_and_display_top5()
    elif Check_time('10:00:00'):
        if Check_week_day('Mon'):
            await sort_and_display_top10()

def Copy_from_csv_to_dict(csv_filename, dict):
    if not os.path.isfile(csv_filename):
        return
    with open(csv_filename, 'r') as csv_file:
        for row in csv.DictReader(csv_file, delimiter=DEFAULT_DELIMITER):
            tmp_dict = row.copy()
            tmp_dict.pop('key')
            tmp_dict['upvote'] = int(tmp_dict['upvote'])
            tmp_dict['downvote'] = int(tmp_dict['downvote'])
            dict[int(row['key'])] = tmp_dict

def Init_dicts():
    Copy_from_csv_to_dict(DAILY_CSV, DAILY_DICT)
    Copy_from_csv_to_dict(WEEKLY_CSV, WEEKLY_DICT)
    print(DAILY_DICT)
    print(WEEKLY_DICT)


def Write_dict_to_temp(DICT, temp_file):
    for key in DICT:
        write = csv.DictWriter(temp_file, fieldnames=DATABASE_FIELDNAMES, restval=key, delimiter=DEFAULT_DELIMITER)
        write.writerow(DICT[key])


def Temp_becomes_database(database_filename, temp_filename):
    Safe_delete_file(database_filename)
    os.rename(temp_filename, database_filename)


def Save_to_csv(local_dict, database_filename):
    temp_filename = 'temp.csv'
    with open(temp_filename, 'w', newline='') as temp:
        write = csv.DictWriter(temp, fieldnames=DATABASE_FIELDNAMES, delimiter=DEFAULT_DELIMITER)
        write.writeheader()
        Write_dict_to_temp(local_dict, temp)
    Temp_becomes_database(database_filename, temp_filename)



__is_time_for_daily = True
@tasks.loop(seconds=150)
async def Backup_csv_database():
    global __is_time_for_daily
    #print('Back-up initializat')
    if __is_time_for_daily:
        Save_to_csv(DAILY_DICT, DAILY_CSV)
        #print('Daily backed-up successfully')
    else:
        Save_to_csv(WEEKLY_DICT, WEEKLY_CSV)
        #print('Weekly backed-up successfully')
    __is_time_for_daily = not __is_time_for_daily