import discord
import copy
from utils import *
from asyncio import sleep
import atexit
import signal

info1 = {}
#print(Get_UTC_time())

@atexit.register
def Handle_exit():
    Save_to_csv(DAILY_DICT, DAILY_CSV)
    Save_to_csv(WEEKLY_DICT, WEEKLY_CSV)

@CLIENT.event
async def on_ready():
    global IS_CONNECTED
    if IS_CONNECTED:
        Init_dicts()
        Print_top_suggestions.start()
        Backup_csv_database.start()
    IS_CONNECTED = 0
    signal.signal(signal.SIGTERM, Handle_exit)
    signal.signal(signal.SIGINT, Handle_exit)
    print('We have logged in as {0.user}'.format(CLIENT))


@CLIENT.event
async def on_message(message):
    if not Check_channel(message.channel.id):
        return
    if message.author == CLIENT.user:
        return
    if message.content.startswith('!s ') or (
            (len(message.content) < 3 or message.content[1] == ' ') and message.content.startswith('!s') and len(
            message.attachments) > 0):
        if len(message.content) > MAX_SUGGESTION_LENGTH + 3:
            await message.channel.send(
                "**I'm sorry {}, but you exceeded the limit of {} characters for a suggestion!**".format(
                    message.author.mention, MAX_SUGGESTION_LENGTH))
            await message.delete()
            return
        message.content = message.content[3:]
    elif message.content.startswith('!sugg ') or (
            (len(message.content) < 6 or message.content[1] == ' ') and message.content.startswith('!sugg') and len(
            message.attachments) > 0):
        if len(message.content) > MAX_SUGGESTION_LENGTH + 6:
            await message.channel.send(
                "**I'm sorry {}, but you exceeded the limit of {} characters for a suggestion!**".format(
                    message.author.mention, MAX_SUGGESTION_LENGTH))
            await message.delete()
            return
        message.content = message.content[6:]
    # elif message.content == '!print':
    #     await sort_and_display_top5()
    #     return
    # elif message.content == '$save':
    #     Save_to_csv(DAILY_DICT, DAILY_CSV)
    #     Save_to_csv(WEEKLY_DICT, WEEKLY_CSV)
    #     return
    else:
        return
    await display_embed(message)
    await message.delete()


async def add_to_database(Embed_msg, message):
    info1.update({'author': message.author.display_name, 'message': message.content})
    DAILY_DICT.update({Embed_msg.id: copy.deepcopy(info1)})
    WEEKLY_DICT.update({Embed_msg.id: copy.deepcopy(info1)})


async def display_embed(message):
    Date = datetime.datetime.utcnow()
    Channel = CLIENT.get_channel(852843140213243945)
    embed = discord.Embed(
        description=message.content,
        colour=discord.Colour.blue()
    )
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
    if message.attachments:
        embed.set_image(url=message.attachments[0].url)
    embed.set_footer(text=Date.strftime("%b %d, %Y"))
    Embed_msg = await Channel.send(embed=embed)
    await Embed_msg.add_reaction(CLIENT.get_emoji(881643747325124678))
    await Embed_msg.add_reaction(CLIENT.get_emoji(881644076661870623))
    await add_to_database(Embed_msg, message)


async def Get_message_by_id(message_id):
    msg = discord.utils.get(CLIENT.cached_messages, id=message_id)
    # #print(msg)
    if msg is None:
        msg = await CLIENT.get_channel(852843140213243945).fetch_message(id=message_id)
        # #print(msg)
    ##print(msg)
    return msg

async def Update_dict_votes(dict, message_id):
    msg = await Get_message_by_id(message_id)
    if msg is None:
        raise
    if len(msg.reactions) >= 2:
        info1.update({'upvote': msg.reactions[0].count, 'downvote': msg.reactions[1].count})
        if message_id in dict:
            dict[message_id]['upvote'] = msg.reactions[0].count
            dict[message_id]['downvote'] = msg.reactions[1].count
        print(dict)

@CLIENT.event
async def on_raw_reaction_add(event):
    try:
        await sleep(0.5)
        await Update_dict_votes(DAILY_DICT, event.message_id)
        await Update_dict_votes(WEEKLY_DICT, event.message_id)
    except:
        pass
        #print('Couldn\'t add reaction to the counter')


@CLIENT.event
async def on_raw_reaction_remove(event):
    try:
        await sleep(0.5)
        await Update_dict_votes(DAILY_DICT, event.message_id)
        await Update_dict_votes(WEEKLY_DICT, event.message_id)
    except:
        pass
        #print('Couldn\'t remove reaction')

CLIENT.run('ODc3NzE4NjkyMDk4NjIxNDQx.YR2tOw.kWD5R27L4kobEA91UbL3EOyNKVc')