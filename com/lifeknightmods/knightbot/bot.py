import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

prefix = '/'

guild = discord.utils.get(client.guilds, id=366700898602188811)


@client.event
async def on_ready():
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
    await memberlog_channel.send(f'Farewell **{member.name}!**')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content[0] == prefix:
        process_command(message.content)


def process_command(arguments):


async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise


client.run(TOKEN)
