import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

prefix = '/'

guild = None


@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, id=366700898602188811)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


@client.event
async def on_member_join(member):
    memberlog_channel = discord.utils.get(guild.channels, id=502619633061462036)
    await memberlog_channel.send(f'Welcome to LifeKnight\'s Discord <@{member.id}>! Please read <#451127347626639361> '
                                 f'and <#465206340730617866> before doing anything!')


@client.event
async def on_member_leave(member):
    memberlog_channel = discord.utils.get(guild.channels, id=502619633061462036)
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
        resource_packs_embed = discord.Embed(title="Resource Packs", description="LifeKnight's resource packs..", color=0xff0000)
        for i in resource_packs:
            resource_packs_embed.add_field(name=i, value=resource_packs[i], inline=False)
        embed_response = resource_packs_embed
    else:
        commands = {
            "/socials": "Lists LifeKnight's accounts.",
            "/mods": "Lists LifeKnight's mods.",
            "/texturepacks": "Lists LifeKnight's texture packs."
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
        f.write(f'There was an error: {args}')


client.run(TOKEN)
