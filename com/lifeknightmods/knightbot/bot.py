import json
import os
import random
import sys
import time
import urllib.request
from googleapiclient.discovery import build

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

prefix = '/'

discord_server_members = []
last_config_read_time = None

knightbot_channel = None

knightbot_response_channel = None

english_word_list = []

last_scrambled_word = None

last_scrambled_time = 0


class Utilities:

    @staticmethod
    async def on_startup():
        await Utilities.read_configuration_file()
        DiscordServerMember.check_for_member_updates()
        await Utilities.update_configuration_file()
        page = urllib.request.urlopen("http://www.desiquintans.com/downloads/nounlist/nounlist.txt")
        global english_word_list
        for line in page:
            if len(line) >= 5:
                as_string = str(line)
                as_string = as_string[2:len(as_string) - 3]
                english_word_list.append(as_string)

        page = urllib.request.urlopen("https://gist.githubusercontent.com/hugsy/8910dc78d208e40de42deb29e62df913/raw"
                                      "/eec99c5597a73f6a9240cab26965a8609fa0f6ea/english-adjectives.txt")
        for line in page:
            if len(line) >= 5:
                as_string = str(line)
                as_string = as_string[2:len(as_string) - 3]
                english_word_list.append(as_string)

    @staticmethod
    def get_current_time_millis():
        return int(round(time.time() * 1000))

    @staticmethod
    async def send_scrambled_message():
        global english_word_list
        random_word = english_word_list[random.randint(0, len(english_word_list) - 1)]
        global last_scrambled_word
        last_scrambled_word = random_word
        scrambled = Utilities.scramble_word(random_word)
        await get_knightbot_channel().send(
            f"Unscramble the message to receive points! **{scrambled}**")
        print(f"Scrambled word: {random_word}")
        global last_scrambled_time
        last_scrambled_time = Utilities.get_current_time_millis()

    @staticmethod
    def scramble_word(word):
        new_word = ""
        indexes_used = []

        while len(new_word) != len(word):
            random_index = Utilities.get_random_number_that_isnt(0, len(word) - 1, indexes_used)
            new_word += word[random_index]
            indexes_used.append(random_index)

        return new_word

    @staticmethod
    def get_random_number_that_isnt(min, max, previous):
        random_value = random.randint(min, max)
        if not random_value in previous:
            return random_value
        return Utilities.get_random_number_that_isnt(min, max, previous)

    @staticmethod
    async def read_configuration_file():
        try:
            with open("configuration.txt", 'r') as file:
                content = file.read()
                data_map = json.loads(content)
                global last_config_read_time
                last_config_read_time = data_map["time"]
                DiscordServerMember.read_members_from_tuple(data_map["members"])
        except:
            await on_error("An error occurred while trying to interpret the configuration file.")

    @staticmethod
    async def update_configuration_file():
        try:
            with open("configuration.txt", 'w') as file:
                data = {
                    "time": Utilities.get_current_time_millis(),
                    "members": DiscordServerMember.get_members_as_tuple(),
                }
                file.write(json.dumps(data, indent=4))
        except:
            await on_error("An error occurred while trying to write to the configuration file.")

    @staticmethod
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
        video_embed.add_field(name="Viewers", value=video_statistics["items"][0]["statistics"]["viewCount"], inline=False)
        video_embed.add_field(name="Likes", value=video_statistics["items"][0]["statistics"]["likeCount"], inline=False)

        video_embed.set_thumbnail(url=video["snippet"]["thumbnails"]["high"]["url"])

        return video_embed

    @staticmethod
    async def exit_bot():
        await Utilities.update_configuration_file()
        sys.exit(0)


class DiscordServerMember:
    def __init__(self, id_in, points_in):
        self.id = id_in
        self.points = points_in
        if self.points is None:
            self.points = 0

        for member in get_guild().members:
            if member.id == self.id:
                self.user = member
                break
        discord_server_members.append(self)

    def get_user(self):
        return self.user

    def get_id(self):
        return self.id

    def get_name(self):
        return self.user.name

    def get_points(self):
        return self.points

    @staticmethod
    def check_for_member_updates():
        for member in get_guild().members:
            if not DiscordServerMember.has_member(member.id):
                DiscordServerMember(member.id, 0)

    @staticmethod
    def has_member(id_in):
        return any([member.get_id() == id_in for member in discord_server_members])

    @staticmethod
    def get_members_as_tuple():
        members = []
        for member in discord_server_members:
            members.append({"id": member.id, "points": member.points})
        return members

    @staticmethod
    def read_members_from_tuple(members):
        for member_map in members:
            DiscordServerMember(member_map["id"], member_map["points"])

    @staticmethod
    def get_by_id_or_name(id_or_name):
        for member in discord_server_members:
            if member.id == id_or_name:
                return member
        for member in discord_server_members:
            if member.get_name().lower() == str(
                    id_or_name).lower() or member.get_user().displayname == id_or_name.lower():
                return member

    @staticmethod
    def add_points_by_id(id_in, points):
        DiscordServerMember.get_by_id_or_name(id_in).points += points

    @staticmethod
    def get_member_with_most_points():
        member_with_most_points = None
        for member in discord_server_members:
            if member_with_most_points is None or member.get_points() > member_with_most_points.get_points():
                member_with_most_points = member

        return member_with_most_points


@client.event
async def on_ready():
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{get_guild().name} (id: {get_guild().id})'
    )
    await Utilities.on_startup()
    await Utilities.send_scrambled_message()


@client.event
async def on_member_join(member):
    memberlog_channel = discord.utils.get(get_guild().channels, id=502619633061462036)
    await memberlog_channel.send(f'Welcome to LifeKnight\'s Discord <@{member.id}>! Please read <#451127347626639361> '
                                 f'and <#465206340730617866> before doing anything!')
    DiscordServerMember.check_for_member_updates()


@client.event
async def on_member_leave(member):
    memberlog_channel = discord.utils.get(get_guild().channels, id=502619633061462036)
    await memberlog_channel.send(f'Farewell **{member.user}!**')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id == get_knightbot_response_channel().id:
        await process_response(message)

    elif len(message.content) > 1 and message.content[0] == prefix:
        await process_command(message, message.content[1:])

    if last_scrambled_time == 0 or last_scrambled_time - Utilities.get_current_time_millis() < -15 * 60 * 1000:
        await Utilities.send_scrambled_message()


async def process_response(message):
    if message.content.lower() == last_scrambled_word:
        random_points = random.randint(1, 3)
        if random_points == 1:
            point_message = "You received **1 point!**"
        else:
            point_message = f"You received **{random_points} points!**"
        DiscordServerMember.add_points_by_id(message.author.id, random_points)
        await get_knightbot_response_channel().send(f"Nice <@{message.author.id}>! {point_message}")

        top_member_id = DiscordServerMember.get_member_with_most_points().get_id()
        for member in discord_server_members:
            user = member.get_user()
            if user.roles.__contains__(get_pointest_role()) and user.id != top_member_id:
                await user.remove_roles(get_pointest_role())
            elif not user.roles.__contains__(get_pointest_role()) and user.id == top_member_id:
                await user.add_roles(get_pointest_role())
                await get_knightbot_response_channel().send(f"Congratulations! You are now the POINTEST!")

        await Utilities.send_scrambled_message()
        await Utilities.update_configuration_file()
        return


async def process_command(message, arguments):
    text_response = None
    embed_response = None
    if arguments.lower() == "social" or arguments.lower() == "socials":
        socials = {
            "YouTube": "https://www.youtube.com/channel/UCGfAdb9d2c7X_5JffTz9hGQ",
            "YouTube (2)": "https://www.youtube.com/channel/UCkQN_DV0aOKwpSmFSJ-xrxw",
            "YouTube (3)": "https://www.youtube.com/channel/UC6tKelwMuyKuHtOHIwBOJag",
            "Twitter": "https://twitter.com/__LifeKnight",
            "Fiverr": "https://www.fiverr.com/share/gvKN4E",
        }
        mods_embed = discord.Embed(title="Socials", description="LifeKnight's social accounts.", color=0xff0000)
        for i in socials:
            mods_embed.add_field(name=i, value=socials[i], inline=False)
        embed_response = mods_embed
    elif arguments.lower() == "mods":
        mods = {
            "Bridging Analysis": "https://youtu.be/_AognfACDmg",
            "ChatControl": "https://youtu.be/oPiPtvjkIM0",
            "Bruh-Stal": "https://youtu.be/XpkPnikgM1M"
        }
        mods_embed = discord.Embed(title="Mods", description="LifeKnight's popular mods.", color=0xff0000)
        for i in mods:
            mods_embed.add_field(name=i, value=mods[i], inline=False)
        embed_response = mods_embed
    elif arguments.lower().replace(" ", "") == "texturepacks" or arguments.lower().replace(" ",
                                                                                           "") == "resourcepacks" or arguments.lower() == "packs":
        resource_packs = {
            "16x Swords, 128x Blocks": "http://www.mediafire.com/file/v20bu2xzzgtyzlf/A_Simple_PvP_Experience%2521_"
                                       "%255BRed_Diamond_Edit%255D.zip/file",
            "Default Red Edit": "http://www.mediafire.com/file/teb5n3f78d8orqo/Default_Texture_Pack_%255BRed_Edit%255D"
                                ".zip/file",
            "64x64 Text (Overlay)": "http://www.mediafire.com/file/qx9sz4fuyjujqmv/faithful_text_64x64.zip/file"
        }
        resource_packs_embed = discord.Embed(title="Resource Packs", description="LifeKnight's resource packs.",
                                             color=0xff0000)
        for i in resource_packs:
            resource_packs_embed.add_field(name=i, value=resource_packs[i], inline=False)
        embed_response = resource_packs_embed
    elif arguments.lower().startswith("profile"):
        if len(arguments.replace(" ", "")) == 7:
            member_profile_embed = discord.Embed(title=f"{message.author.name}", description="Your KnightBot profile.",
                                                 color=0xff0000)
            member = DiscordServerMember.get_by_id_or_name(message.author.id)
            member_profile_embed.add_field(name="Points", value=str(member.get_points()), inline=True)
            embed_response = member_profile_embed
        else:
            try:
                member_id_or_name = arguments.split(" ")[1]
                if member_id_or_name.startswith("<@"):
                    member_id_or_name = int(member_id_or_name[2:len(member_id_or_name) - 1])
                elif member_id_or_name.isnumeric():
                    member_id_or_name = int(member_id_or_name)

                member = DiscordServerMember.get_by_id_or_name(member_id_or_name)
                member_profile_embed = discord.Embed(title=member.get_name(),
                                                     description=f"<@{member.get_id()}>'s KnightBot profile.",
                                                     color=0xff0000)
                member_profile_embed.add_field(name="Points", value=str(member.get_points()), inline=True)
                embed_response = member_profile_embed
            except:
                text_response = "No user found."
    elif arguments.lower() == "leaderboard":
        top = []
        members = discord_server_members
        while len(top) < 11:
            member_with_most_points = None
            for member in members:
                if member_with_most_points is None or member.get_points() > member_with_most_points.get_points():
                    member_with_most_points = member
            top.append(member_with_most_points)
            members.remove(member_with_most_points)

        leaderboard_embed = discord.Embed(title="Leaderboard", description="KnightBot points leaderboard.",
                                          color=0xff0000)
        for i in range(len(top)):
            member = top[i]
            leaderboard_embed.add_field(name=f"#{i + 1} - {member.get_name()}",
                                        value=f"{str(member.get_points())} points", inline=False)
        embed_response = leaderboard_embed
    elif arguments.lower().replace(" ", "") == "randomstreamer" or arguments.lower() == "streamer":
        try:
            embed_response = await Utilities.get_random_stream()
        except:
            text_response = "An error occured. Please try again."
            await on_error("Error while fetching random streamer.")
    else:
        commands = {
            "/socials": "Lists LifeKnight's accounts.",
            "/mods": "Lists LifeKnight's mods.",
            "/resourcepacks": "Lists LifeKnight's resource packs.",
            "/profile [user]": "Returns the KnightBot profile of the user.",
            "/leaderboard": "Displays the KnightBot-point leaderboard.",
            "/randomstreamer": "Returns a random streamer.",
        }
        commands_embed = discord.Embed(title="Commands", description="Commands for this bot.", color=0xff0000)
        for i in commands:
            commands_embed.add_field(name=i, value=commands[i], inline=False)
        embed_response = commands_embed

    if text_response is not None:
        await message.channel.send(text_response)
    elif embed_response is not None:
        await message.channel.send(embed=embed_response)


async def on_error(event, *args, **kwargs):
    print(f'There was an error: {event} - {args} - {kwargs}\n')
    with open('err.log', 'a') as f:
        f.write(f'There was an error: {event} - {args} - {kwargs}\n')


def get_guild():
    return discord.utils.get(client.guilds, id=366700898602188811)


def get_knightbot_channel():
    return discord.utils.get(get_guild().channels, id=734409425430773850)


def get_knightbot_response_channel():
    return discord.utils.get(get_guild().channels, id=734413328075587644)


def get_pointest_role():
    for role in get_guild().roles:
        if role.id == 734507294980571258:
            return role


client.run(TOKEN)

"""
IDEAS

/up, gives you points, person with most up gets the up role
    - role editing
    - perhaps you have to wait a random amount of time and if you wait to long or too short you will receive a penalty
    - unscramble, a channel for the bot to send messages
"""
