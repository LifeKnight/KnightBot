import datetime
import random
import time

import discord
from googleapiclient.discovery import build

import bot_commands
from member_utilities import add_points_by_id, get_member_with_most_points, discord_server_members

CLIENT = None

english_word_list = []
last_question_time = 0
last_question_response = None


def set_client(client_in):
    global CLIENT
    CLIENT = client_in


async def on_message(message):
    if message.channel.id == get_knightbot_response_channel().id:
        await process_response(message)

    elif len(message.content) > 1 and message.content[0] == '/':
        await bot_commands.process_command(message, message.content[1:])

    if last_question_time == 0 or last_question_time - get_current_time_millis() < -15 * 60 * 1000:
        await send_question()


def get_current_time_millis():
    return int(round(time.time() * 1000))


def scramble_word(word):
    new_word = ""
    indexes_used = []

    while len(new_word) != len(word):
        random_index = get_random_number_that_isnt(0, len(word) - 1, indexes_used)
        new_word += word[random_index]
        indexes_used.append(random_index)

    return new_word


def get_random_number_that_isnt(min, max, previous):
    random_value = random.randint(min, max)
    if random_value not in previous:
        return random_value
    return get_random_number_that_isnt(min, max, previous)


async def get_random_stream():
    developer_key = 'AIzaSyA-dBiqrzPhCbkiWQCtWh2T-UYkcil05ds'
    youtube_api_service_name = 'youtube'
    youtube_api_version = 'v3'

    youtube = build(youtube_api_service_name, youtube_api_version,
                    developerKey=developer_key)

    search_response = youtube.search().list(
        part="snippet",
        eventType="live",
        maxResults=25,
        order="viewCount",
        q="hypixel,/p join,/party join",
        type="video"
    ).execute()

    videos = search_response["items"]

    video = videos[random.randint(0, len(videos) - 1)]

    video_statistics = youtube.videos().list(
        part="statistics",
        id=video["id"]["videoId"]
    ).execute()

    video_embed = discord.Embed(title="Random Stream - " + video["snippet"]["title"],
                                description=video["snippet"]["channelTitle"], color=0xff0000)

    video_embed.add_field(name="Link", value="https://www.youtube.com/watch?v=" + video["id"]["videoId"],
                          inline=False)
    video_embed.add_field(name="Description", value=video["snippet"]["description"], inline=False)
    video_embed.add_field(name="Viewers", value=video_statistics["items"][0]["statistics"]["viewCount"],
                          inline=False)
    video_embed.add_field(name="Likes", value=video_statistics["items"][0]["statistics"]["likeCount"], inline=False)

    video_embed.set_thumbnail(url=video["snippet"]["thumbnails"]["high"]["url"])

    return video_embed


def get_current_time_string():
    now = datetime.datetime.now()
    return now.strftime("%m/%d/%y %H:%M:%S")


def get_guild():
    return discord.utils.get(CLIENT.guilds, id=366700898602188811)


def get_knightbot_channel():
    return discord.utils.get(get_guild().channels, id=734409425430773850)


def get_knightbot_response_channel():
    return discord.utils.get(get_guild().channels, id=734413328075587644)


def get_pointest_role():
    for role in get_guild().roles:
        if role.id == 734507294980571258:
            return role


async def send_question():
    random_integer = random.randint(0, 1)
    global last_question_response

    if random_integer == 0:
        global english_word_list
        random_word = english_word_list[random.randint(0, len(english_word_list) - 1)]
        last_question_response = random_word
        scrambled = scramble_word(random_word)
        await get_knightbot_channel().send(
            f"Unscramble the word to receive points! **{scrambled}**")
    else:
        random_integer_2 = random.randint(0, 3)
        if random_integer_2 == 0:
            operation = '+'
            num1 = random.randint(50, 500)
            num2 = random.randint(50, 500)
            last_question_response = str(num1 + num2)
        elif random_integer_2 == 1:
            operation = '-'
            num1 = random.randint(50, 500)
            num2 = random.randint(50, 500)
            last_question_response = str(num1 - num2)
        elif random_integer_2 == 2:
            operation = '*'
            num1 = random.randint(7, 20)
            num2 = random.randint(11, 25)
            last_question_response = str(num1 * num2)
        else:
            operation = '//'
            num1 = random.randint(50, 500)
            num2 = random.randint(7, 15)
            last_question_response = str(num1 // num2)
        await get_knightbot_channel().send(f"Simplify this expression to receive points! **{num1} {operation} {num2}**")
    global last_question_time
    last_question_time = get_current_time_millis()
    print(f"Answer: {last_question_response}")


async def process_response(message):
    if message.content.lower() == last_question_response:
        random_points = random.randint(1, 3)
        if random_points == 1:
            point_message = "You received **1 point!**"
        else:
            point_message = f"You received **{random_points} points!**"
        add_points_by_id(message.author.id, random_points)
        await get_knightbot_response_channel().send(f"Nice <@{message.author.id}>! {point_message}")

        top_member_id = get_member_with_most_points().get_member_id()
        for member in discord_server_members:
            if member.has_user():
                user = member.get_user()
                pointest_role = get_pointest_role()
                if user.roles.__contains__(pointest_role) and user.id != top_member_id:
                    await user.remove_roles(pointest_role)
                elif not user.roles.__contains__(pointest_role) and user.id == top_member_id:
                    await user.add_roles(pointest_role)
                    await get_knightbot_response_channel().send(f"Congratulations! You are now the "
                                                                f"POINTEST!")

        await send_question()
        return
