import discord

CLIENT = None

discord_server_members = []


def set_client(client_in):
    global CLIENT
    CLIENT = client_in


class DiscordServerMember:
    def __init__(self, id_in, points_in):
        self.id = id_in
        self.points = points_in
        if self.points is None:
            self.points = 0
        discord_server_members.append(self)

    def get_user(self):
        for member in get_guild().members:
            if member.id == self.id:
                return member

    def has_user(self):
        return any([member.id == self.id for member in get_guild().members])

    def get_member_id(self):
        return self.id

    def get_name(self):
        return self.get_user().name

    def get_points(self):
        return self.points

    def add_to_points(self, points):
        self.points += points


def has_member(id_in):
    return any([member.id == id_in for member in discord_server_members])


def check_for_member_updates():
    for member in get_guild().members:
        if not has_member(member.id) and not member.bot:
            DiscordServerMember(member.id, 0)


def read_members_from_tuple(members):
    for member_map in members:
        DiscordServerMember(member_map["id"], member_map["points"])


def get_by_id_or_name(id_or_name):
    for member in discord_server_members:
        if member.id == id_or_name:
            return member
    for member in discord_server_members:
        if member.has_user() and member.get_name().lower() == str(
                id_or_name).lower() or (
                member.has_user() and member.get_user().display_name == str(id_or_name).lower()):
            return member


def add_points_by_id(id_in, points):
    get_by_id_or_name(id_in).add_to_points(points)


def get_member_with_most_points():
    member_with_most_points = None
    for member in discord_server_members:
        if member_with_most_points is None or member.get_points() > member_with_most_points.get_points():
            member_with_most_points = member
    return member_with_most_points


def get_members_as_tuple():
    members = []
    for member in discord_server_members:
        member_id = member.get_member_id()
        member_points = member.get_points()
        members.append({
            "id": member_id,
            "points": member_points,
            "name": member.get_name() if member.has_user() else "None"})
    return members


def get_guild():
    return discord.utils.get(CLIENT.guilds, id=366700898602188811)
