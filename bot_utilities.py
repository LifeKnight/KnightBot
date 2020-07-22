import datetime
import random
import time

import discord
from googleapiclient.discovery import build


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
    if not random_value in previous:
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
