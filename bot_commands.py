import discord
import abc

from member_utilities import get_by_id_or_name

commands = []


def dummy():
    return "dummy"


class Command:
    def __init__(self, name, aliases):
        self.name = name
        self.aliases = aliases
        self.response = response

    @property
    def get_aliases(self):
        return self.aliases

    @abc.abstractmethod
    def process_command(self, arguments):
        return


def create_commands():
    Command("Social", ["social", "socials"])


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
        socials_embed = discord.Embed(title="Socials", description="LifeKnight's social accounts.", color=0xff0000)
        for i in socials:
            socials_embed.add_field(name=i, value=socials[i], inline=False)
        embed_response = socials_embed
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
            member = get_by_id_or_name(message.author._id)
            member_profile_embed.add_field(name="Points", value=str(member.get_points()), inline=True)
            embed_response = member_profile_embed
        else:
            try:
                member_id_or_name = arguments.split(" ")[1]
                if member_id_or_name.startswith("<@"):
                    member_id_or_name = int(member_id_or_name[2:len(member_id_or_name) - 1])
                elif member_id_or_name.isnumeric():
                    member_id_or_name = int(member_id_or_name)

                member = get_by_id_or_name(member_id_or_name)
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
            embed_response = await bot_utilities.get_random_stream()
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
