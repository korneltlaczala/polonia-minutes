import copy
import datetime
import os
import json
from . import util

class Club:
    def __init__(self, name, folder):
        self.name = name
        self.folder = "data/" + folder
        self.leagues = []
        self.load_teams()
        self.load_leagues()

    def prep_stats(self, active_leagues=None):
        self.load_players()
        for league in self.leagues:
            if active_leagues is None or len(active_leagues) == 0 or league.id in active_leagues:
                league.prep_stats()

    def read_teams(self):
        with open(f"{self.folder}/teams.json", "r", encoding="utf-8") as f:
            teams = json.load(f)
        return teams

    def load_teams(self):
        self.teams = []
        teams = self.read_teams()
        for team in teams:
            self.teams.append(Team(self,
                                   team["id"],
                                   team["category"],
                                   team["category_age"]))

    def read_leagues(self):
        with open(f"{self.folder}/leagues.json", "r", encoding="utf-8") as f:
            leagues = json.load(f)
        return leagues

    def load_leagues(self):
        self.leagues = []
        leagues = self.read_leagues()
        for league in leagues:
            self.leagues.append(League(self,
                                       league["name"],
                                       league["folder"],
                                       league["category"],
                                       league["url"]))

    def load_players(self):
        self.players = []
        for league in self.leagues:
            players = league.read_players()
            for player in players:
                self.try_add_player(player, league)

    def try_add_player(self, player, league):
        id = player["id"]
        firstname = player["firstname"]
        lastname = player["lastname"]
        isKeeper = player["isKeeper"]

        for p in self.players:
            if p.id == id:
                p.add_league(league)
                return
        player = Player(id, firstname, lastname, isKeeper)
        player.add_league(league)
        self.players.append(player)

    def get_team(self, id):
        for team in self.teams:
            if team.id == id:
                return team

    def get_player(self, id):
        for player in self.players:
            if player.id == id:
                return player

    def show_players(self):
        for player in self.players:
            player.show_minutes()

    def show_teams(self):
        for team in self.teams:
            print(team)

    def show_leagues(self):
        for league in self.leagues:
            print(league)

    def download_matches(self):
        for league in self.leagues:
            league.download_matches()

    def download_players(self):
        for league in self.leagues:
            league.download_players()

    def download_match_data(self):
        for league in self.leagues:
            league.download_match_data()

    def repair_matches(self):
        for league in self.leagues:
            league.repair_matches()

    def get_players_for_team(self, team_id, active_leagues=None):
        self.folder = self.folder[(self.folder.rfind("/") + 1):]
        tempClub = Club(self.name, self.folder)
        tempClub.prep_stats(active_leagues=active_leagues)
        team_id = int(team_id)
        team = tempClub.get_team(team_id)
        print(team)
        players = []
        for player in tempClub.players:
            if player.belongs_to_team(team):
                players.append(player)

        return players

    def __str__(self):
        output = ""
        for team in self.teams:
            output += team.__str__()
            output += "\n"
            for league in team.leagues:
                output += f"\t{league}\n"

        return output

class Team:
    def __init__(self, club, id, category, category_age):
        self.club = club
        self.id = id
        self.category = category
        self.category_age = category_age

    @property
    def leagues(self):
        leagues = []
        for league in self.club.leagues:
            if league.category == self.category:
                leagues.append(league)
        return leagues

    @property
    def players(self):
        players = []
        for player in self.club.players:
            if player.belongs_to_team(self):
                players.append(player)
        return players

    @property
    def active_leagues(self):
        leagues = []
        for player in self.players:
            for league in player.leagues:
                if league.age < self.age:
                    continue
                if league in leagues:
                    continue
                leagues.append(league)
        return leagues

    @property
    def age(self):
        return int(self.category_age[2:])

    @property
    def birthyear(self):
        return datetime.date.today().year - self.age

    def __str__(self):
        return f"{self.category}, {self.category_age}"

class League:
    def __init__(self, club, name, folder, category, url):
        self.club = club
        self.name = name
        self.folder = folder
        self.category = category
        self.url = url

        self.not_played_matches = []
        self.played_matches = []

    def prep_stats(self):
        self.load_played_matches()
        for match in self.played_matches:
            match.prep_stats()

    def read_players(self):
        dir = os.path.join(self.club.folder, self.folder)
        with open(os.path.join(dir, "players.json"), "r", encoding="utf-8") as f:
            players = json.load(f)
        return players

    def read_played_matches(self):
        return self.read_matches("played-matches.json")

    def read_not_played_matches(self):
        return self.read_matches("not-played-matches.json")

    def read_matches(self, filename):
        dir = os.path.join(self.club.folder, self.folder)
        with open(os.path.join(dir, filename), "r", encoding="utf-8") as f:
            matches = json.load(f)
        return matches

    def load_matches(self):
        self.load_played_matches()
        self.load_not_played_matches()

    def load_played_matches(self):
        played_matches = self.read_played_matches()
        self.played_matches = []
        self.matches_to_objects(played_matches, self.played_matches)
    
    def load_not_played_matches(self):
        not_played_matches = self.read_not_played_matches()
        self.not_played_matches = []
        self.matches_to_objects(not_played_matches, self.not_played_matches)

    def matches_to_objects(self, match_list, match_object_list):
        for match in match_list:
            match_object_list.append(Match(self.club,
                                          self,
                                          match["matchId"],
                                          match["state"],
                                          match["dateTime"],
                                          match["canDateTimeChange"],
                                          match["scores"],
                                          match["host"],
                                          match["guest"],
                                          match["league"],
                                          match["play"]))

    def show_matches(self):
        print(f"Played matches:")
        for match in self.played_matches:
            print(match)
        print(f"Not played matches:")
        for match in self.not_played_matches:
            print(match)
        print(f"\n")

    def show_players(self, show_zeros=False):
        print("="*20)
        print(self)
        print("Players:")
        list = []
        for player in self.club.players:
            if self not in player.leagues:
                continue
            if not show_zeros and player.apps == 0:
                continue
            list.append(player)

        for player in sorted(list, key=lambda player: player.minutes, reverse=True):
            player.show_minutes()

    def download_matches(self):
        dir = os.path.join(self.club.folder, self.folder)
        util.prep_dir(dir)
        util.catch_and_save_files(self.url, ["played-matches", "not-played-matches"], dir)
        self.repair_matches()

    def download_players(self, force=False):
        if self.players_downloaded() and not force:
            print(f"Players already downloaded for {self}")
            return
        print(f"Downloading players for {self}...")
        dir = os.path.join(self.club.folder, self.folder)
        util.prep_dir(dir)
        util.catch_and_save_files(self.url, ["players"], dir)

    def download_match_data(self, force=False):
        self.load_matches()
        for match in self.played_matches:
            if not match.events_downloaded() or force:
                print(match)
                match.download_events()

    def repair_matches(self):
        files_to_repair = ["played-matches.json", "not-played-matches.json"]
        for file in files_to_repair:
            self.repair_matches_file(file)

    def repair_matches_file(self, file):
        dir = os.path.join(self.club.folder, self.folder)
        matches = self.read_matches(file)
        for match in matches:
            if "abbreviation" not in match["host"]:
                match["host"]["abbreviation"] = match["host"]["name"][:3].upper()
                print(f"adding abbreviation to {match['host']['name']}: {match['host']['abbreviation']}")
            if "abbreviation" not in match["guest"]:
                match["guest"]["abbreviation"] = match["guest"]["name"][:3].upper()
                print(f"adding abbreviation to {match['guest']['name']}: {match['guest']['abbreviation']}")

            if match["host"]["abbreviation"] == match["guest"]["abbreviation"]:
                if "Polonia" in match["host"]["name"] and "Warszawa" in match["host"]["name"]:
                    match["guest"]["abbreviation"] = f"_{match['guest']['abbreviation'][:2]}"
                if "Polonia" in match["guest"]["name"] and "Warszawa" in match["guest"]["name"]:
                    match["host"]["abbreviation"] = f"_{match['host']['abbreviation'][:2]}"

        util.dump_json(dir, file, matches)

    def players_downloaded(self):
        dir = os.path.join(self.club.folder, self.folder)
        return os.path.exists(os.path.join(dir, "players.json"))

    @property
    def team(self):
        for team in self.club.teams:
            if team.category == self.category:
                return team

    @property
    def age(self):
        return self.team.age

    @property
    def id(self):
        return self.folder

    def __str__(self):
        return self.name
        # return f"{self.name:<30} {self.folder}"

    def __repr__(self):
        return f"League(name={self.name}, folder={self.folder})"

    def __eq__(self, other):
        if not isinstance(other, League):
            return False
        return self.folder == other.folder


class Match:
    def __init__(self, club, league, matchId, state, dateTime, canDateTimeChange, scores, host, guest, league_data, play):
        self.club = club
        self.league = league
        self.matchId = matchId
        self.state = state
        self.dateTime = dateTime
        self.canDateTimeChange = canDateTimeChange
        self.scores = scores
        self.host = host
        self.guest = guest
        self.league_data = league_data
        self.play = play

        self.events = None

    def events_downloaded(self):
        match_dir = os.path.join(self.club.folder, self.league.folder, self.id)
        return os.path.exists(os.path.join(match_dir, "events.json"))

    def load_events(self):
        match_dir = os.path.join(self.club.folder, self.league.folder, self.id)
        with open(os.path.join(match_dir, "events.json"), "r", encoding="utf-8") as f:
            self.events = json.load(f)

    def events_downloaded(self):
        match_dir = os.path.join(self.club.folder, self.league.folder, self.id)
        return os.path.exists(os.path.join(match_dir, "events.json"))

    def prep_stats(self):
        if not self.events_downloaded():
            return

        self.load_events()
        if self.host["abbreviation"] == "POL":
            players = self.events["host"]["squad"]
        else:
            players = self.events["guest"]["squad"]

        for player in players:
            p = self.club.get_player(player["id"])
            if p is None:
                self.club.try_add_player(player, self.league)
                p = self.club.get_player(player["id"])
            appearance = Appearance(self.league,
                                    self,
                                    player["type"],
                                    player["number"],
                                    player["isCaptain"],
                                    player["isKeeper"],
                                    player["isJunior"],
                                    player["goals"],
                                    player["cards"],
                                    player["substitutions"])
            try:
                p.add_appearance(appearance)
            except:
                print(f"Error adding appearance to {p}")
                print(player)

    def download_events(self):
        print(f"Downloading events for {self}")
        print(f"from {self.url}")
        match_dir = os.path.join(self.club.folder, self.league.folder, self.id)
        util.prep_dir(match_dir)
        util.catch_and_save_files(self.url, ["events"], match_dir)

    @property
    def id(self):
        abbr = "abbreviation"
        return self.host[abbr] + self.guest[abbr]

    @property
    def url(self):
        return f"https://laczynaspilka.pl/rozgrywki/mecz/{self.matchId}"

    def __str__(self):
        rpr = "abbreviation"
        if self.state == "Nierozegrany":
            return f"{self.host[rpr]} vs {self.guest[rpr]}"
        return f"{self.host[rpr]} {self.scores['final']} {self.guest[rpr]}"

    def __repr__(self):
        rpr = "abbreviation"
        return f"Match(Host={self.host[rpr]}, Guest={self.guest[rpr]}, State={self.state})"

class Player:

    def __init__(self, id, firstname, lastname, isKeeper):
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.isKeepeer = isKeeper

        self.leagues = []
        self.appearances = []

    def add_league(self, league):
        self.leagues.append(league)

    def add_appearance(self, appearance):
        self.appearances.append(appearance)
        self.appearances = sorted(self.appearances, key=lambda app: app.match.dateTime)

    @property
    def apps(self):
        return len([app for app in self.appearances if app.played])

    @property
    def callings(self):
        return len(self.appearances)

    @property
    def minutes(self):
        return sum([app.duration for app in self.appearances if app.played])

    @property
    def active_leagues(self):
        leagues = []
        for app in self.appearances:
            if not app.played:
                continue
            if app.league in leagues:
                continue
            leagues.append(app.league)
        return leagues

    def get_inline_apps(self):
        return f"{self.apps}/{self.callings} apps | {' | '.join([f'{str(app):<20}' for app in self.appearances])}"

    def show_minutes(self):
        print(f"{self.firstname + ' ' + self.lastname:<25} {self.minutes:<4} min | {self.get_inline_apps()}")

    def belongs_to_league(self, league):
        return league in self.leagues

    def belongs_to_team(self, team):
        return team in [league.team for league in self.leagues]

    def __str__(self):
        return f"{self.firstname + ' ' + self.lastname:<25}"


class Appearance:

    def __init__(self, league, match, app_type, number, isCaptain, isKeeper, isJunior, goals, cards, substitutions):
        self.league = league
        self.match = match
        self.app_type = app_type
        self.number = number
        self.isCaptain = isCaptain
        self.isKeeper = isKeeper
        self.isJunior = isJunior
        self.goals = goals
        self.cards = cards
        self.substitutions = substitutions

        self.played = True
        self.process()

    def process(self):
        self.minute_in = 1
        self.minute_out = 90

        for substitution in self.substitutions:
            minute_data = substitution["minute"].split("'")
            minute = int(minute_data[0])
            if len(minute_data) == 3:
                added = int(minute_data[1][2:])
            else:
                added = 0
             
            if substitution["type"].lower() == "in":
                self.minute_in = minute
            elif substitution["type"].lower() == "out":
                self.minute_out = minute-1

        if self.app_type == "Substitute" and len(self.substitutions) == 0:
            self.played = False
            self.minute_in = 91


    @property
    def duration(self):
        return self.minute_out - self.minute_in + 1

    def __str__(self):
        return f"{self.match} ({self.duration} min)"

    def __repr__(self):
        return f"Appearance({self.league}, {self.match}, {self.app_type}, {self.number}, {self.isCaptain}, {self.isKeeper}, {self.isJunior}, {self.goals}, {self.cards}, {self.substitutions})"


if __name__ == "__main__":
    club = Club("Polonia Warszawa", "polonia")
    # print(club)
    # club.download_matches()
    # club.download_players()
    # club.download_match_data()

    club.prep_stats()
    league = club.leagues[0]
    league.show_players()