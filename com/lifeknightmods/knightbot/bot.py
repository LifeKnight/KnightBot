import json
import os
import sys
import time

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

prefix = '/'

discord_server_members = []
last_config_read_time = None


class Utilities:

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
                    "time": int(round(time.time() * 1000)),
                    "members": DiscordServerMember.get_members_as_tuple(),
                }
                file.write(json.dumps(data, indent=4))
        except:
            await on_error("An error occurred while trying to write to the configuration file/")

    @staticmethod
    async def exit_bot():
        await Utilities.update_configuration_file()
        sys.exit(0)


class DiscordServerMember:
    def __init__(self, id_in):
        self.id = id_in
        discord_server_members.append(self)

    def get_id(self):
        return self.id

    def get_name(self):
        for member in get_guild().members:
            if member.id == self.id:
                return member.name

    @staticmethod
    def check_for_member_updates():
        for member in get_guild().members:
            if not DiscordServerMember.has_member(member.id):
                DiscordServerMember(member.id)

    @staticmethod
    def has_member(id_in):
        return any([member.get_id() == id_in for member in discord_server_members])

    @staticmethod
    def get_members_as_tuple():
        members = []
        for member in discord_server_members:
            members.append({"id": member.get_id()})
        return members

    @staticmethod
    def read_members_from_tuple(members):
        for member_string in members:
            DiscordServerMember(member_string["id"])


@client.event
async def on_ready():
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{get_guild().name} (id: {get_guild().id})'
    )

    await Utilities.read_configuration_file()
    DiscordServerMember.check_for_member_updates()
    await Utilities.update_configuration_file()


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

    if len(message.content) > 1 and message.content[0] == prefix:
        await process_command(message.channel, message.content[1:])


async def process_command(channel, arguments):
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
    elif arguments.lower().replace(" ", "") == "texturepacks" or arguments.lower().replace(" ", "") == "packs":
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
    else:
        commands = {
            "/socials": "Lists LifeKnight's accounts.",
            "/mods": "Lists LifeKnight's mods.",
            "/resourcepacks": "Lists LifeKnight's resource packs."
        }
        commands_embed = discord.Embed(title="Commands", description="Commands for this bot.", color=0xff0000)
        for i in commands:
            commands_embed.add_field(name=i, value=commands[i], inline=False)
        embed_response = commands_embed

    if text_response is not None:
        await channel.send(text_response)
    elif embed_response is not None:
        await channel.send(embed=embed_response)


async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        f.write(f'There was an error: {event} - {args} - {kwargs}\n')


def get_guild():
    return discord.utils.get(client.guilds, id=366700898602188811)


client.run(TOKEN)

"""
IDEAS

/up, gives you points, person with most up gets the up role
    - role editing
    - perhaps you have to wait a random amount of time and if you wait to long or too short you will receive a penalty

"""
