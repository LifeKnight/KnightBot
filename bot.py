import json
import os
import sys
import urllib.request

import discord
from dotenv import load_dotenv

import bot_commands
import bot_utilities
import member_utilities
from bot_utilities import send_question, get_current_time_millis, process_response
from member_utilities import check_for_member_updates, \
    read_members_from_tuple, get_members_as_tuple

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

CLIENT = discord.Client()

prefix = '/'


last_config_read_time = 0


async def read_configuration_file():
    try:
        with open("configuration.txt", 'r') as file:
            content = file.read()
            data_map = json.loads(content)
            global last_config_read_time
            last_config_read_time = data_map["time"]
            read_members_from_tuple(data_map["members"])
    except Exception as e:
        await on_error("An error occurred while trying to parse the contents of the configuration file.", e.args)


async def update_configuration_file():
    with open("configuration.txt", 'w') as file:
        data = {
            "time": get_current_time_millis(),
            "members": get_members_as_tuple(),
        }
        file.write(json.dumps(data, indent=4))


async def on_startup():
    await read_configuration_file()
    check_for_member_updates()
    await update_configuration_file()
    page = urllib.request.urlopen("http://www.desiquintans.com/downloads/nounlist/nounlist.txt")
    for line in page:
        if len(line) >= 5:
            as_string = str(line)
            as_string = as_string[2:len(as_string) - 3]
            bot_utilities.english_word_list.append(as_string)

    page = urllib.request.urlopen("https://gist.githubusercontent.com/hugsy/8910dc78d208e40de42deb29e62df913/raw"
                                  "/eec99c5597a73f6a9240cab26965a8609fa0f6ea/english-adjectives.txt")
    for line in page:
        if len(line) >= 5:
            as_string = str(line)
            as_string = as_string[2:len(as_string) - 3]
            bot_utilities.english_word_list.append(as_string)


async def exit_bot():
    await update_configuration_file()
    sys.exit(0)


@CLIENT.event
async def on_ready():
    bot_utilities.set_client(CLIENT)
    member_utilities.set_client(CLIENT)
    print(
        f'{CLIENT.user} is connected to the following guild:\n'
        f'{bot_utilities.get_guild().name} (id: {bot_utilities.get_guild().id})'
    )
    await on_startup()
    await send_question()


@CLIENT.event
async def on_member_join(member):
    memberlog_channel = discord.utils.get(get_guild().channels, id=502619633061462036)
    await memberlog_channel.send(f'Welcome to LifeKnight\'s Discord <@{member.id}>! Please read <#451127347626639361> '
                                 f'and <#465206340730617866> before doing anything!')
    check_for_member_updates()


@CLIENT.event
async def on_member_remove(member):
    memberlog_channel = discord.utils.get(get_guild().channels, id=502619633061462036)
    await memberlog_channel.send(f'Farewell **{member.user}!**')


@CLIENT.event
async def on_message(message):
    if message.author == CLIENT.user:
        return
    await bot_utilities.on_message(message)
    await update_configuration_file()


async def on_error(event, *args, **kwargs):
    print(f'[{bot_utilities.get_current_time_string()}] There was an error: {event} - {args} - {kwargs}\n')
    with open('err.log', 'a') as f:
        f.write(f'[{bot_utilities.get_current_time_string()}] There was an error: {event} - {args} - {kwargs}\n')


CLIENT.run(TOKEN)

"""
IDEAS

/up, gives you points, person with most up gets the up role
    - role editing
    - perhaps you have to wait a random amount of time and if you wait to long or too short you will receive a penalty
    - unscramble, a channel for the bot to send messages
"""


