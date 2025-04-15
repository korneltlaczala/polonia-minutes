import copy
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

    def prep_stats(self):
        self.load_players()
        for league in self.leagues:
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

    def get_players_for_team(self, team_id):
        team_id = int(team_id)
        team = self.get_team(team_id)
        players = []
        for player in self.players:
            if player.belongs_to_team(team):
                players.append(player)

        return players

    def __str__(self):
        output = ""
        for team in self.teams:
            output += team.__str__()
            output += "\n"
            for league in team.get_leagues():
                output += f"\t{league}\n"

        return output

class Team:
    def __init__(self, club, id, category, category_age):
        self.club = club
        self.id = id
        self.category = category
        self.category_age = category_age

    def get_leagues(self):
        leagues = []
        for league in self.club.leagues:
            if league.category == self.category:
                leagues.append(league)
        return leagues

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
        dir = os.path.join(self.club.folder, self.folder)
        with open(os.path.join(dir, "played-matches.json"), "r", encoding="utf-8") as f:
            played_matches = json.load(f)
        return played_matches

    def read_not_played_matches(self):
        dir = os.path.join(self.club.folder, self.folder)
        with open(os.path.join(dir, "not-played-matches.json"), "r", encoding="utf-8") as f:
            not_played_matches = json.load(f)
        return not_played_matches

    def load_matches(self):
        self.load_played_matches()
        self.load_not_played_matches()

    def load_played_matches(self):
        played_matches = self.read_played_matches()
        self.played_matches = []
        for match in played_matches:
            self.played_matches.append(Match(self.club,
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
    
    def load_not_played_matches(self):
        not_played_matches = self.read_not_played_matches()
        self.not_played_matches = []
        for match in not_played_matches:
            self.not_played_matches.append(Match(self.club,
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

    def players_downloaded(self):
        dir = os.path.join(self.club.folder, self.folder)
        return os.path.exists(os.path.join(dir, "players.json"))

    @property
    def team(self):
        for team in self.club.teams:
            if team.category == self.category:
                return team

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
        try:
            with open(os.path.join(match_dir, "events.json"), "r", encoding="utf-8") as f:
                events = json.load(f)
        except FileNotFoundError:
            events = []
        self.events = events

    def prep_stats(self):
        # print(self)
        self.load_events()
        if self.host["abbreviation"] == "POL":
            players = self.events["host"]["squad"]
        else:
            players = self.events["guest"]["squad"]

        for player in players:
            p = self.club.get_player(player["id"])
            # print("\t", f"{p.firstname + ' ' + p.lastname:<24}", end="")
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
            # print(f"{appearance.duration} min")
            p.add_appearance(appearance)

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
            if substitution["type"].lower() == "in":
                self.minute_in = int(substitution["minute"][:-1])
            elif substitution["type"].lower() == "out":
                self.minute_out = int(substitution["minute"][:-1])-1

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