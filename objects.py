import os
import json

class Club:
    def __init__(self, name, folder):
        self.name = name
        self.folder = folder
        self.teams = []
        self.load_teams()
        self.load_players()

    def prep_stats(self):
        for team in self.teams:
            team.prep_stats()

    def read_teams(self):
        with open(f"{self.folder}/teams.json", "r", encoding="utf-8") as f:
            teams = json.load(f)
        return teams

    def load_teams(self):
        self.teams = []
        teams = self.read_teams()
        for team in teams:
            self.teams.append(Team(self, team["name"], team["folder"], team["url"]))

    def load_players(self):
        self.players = []
        for team in self.teams:
            players = team.read_players()
            for player in players:
                self.try_add_player(player, team)

    def try_add_player(self, player, team):
        id = player["id"]
        firstname = player["firstname"]
        lastname = player["lastname"]
        isKeeper = player["isKeeper"]

        for p in self.players:
            if p.id == id:
                p.add_team(team)
                return
        player = Player(id, firstname, lastname, isKeeper)
        player.add_team(team)
        self.players.append(player)

    def get_player(self, id):
        for player in self.players:
            if player.id == id:
                return player

    def show_players(self):
        for player in self.players:
            print(player)

class Team:
    def __init__(self, club, name, folder, url):
        self.club = club
        self.name = name
        self.folder = folder
        self.url = url
        self.not_played_matches = []
        self.played_matches = []

    def prep_stats(self):
        self.load_played_matches()
        for match in self.played_matches:
            match.prep_stats()

    def read_players(self):
        team_dir = os.path.join(self.club.folder, self.folder)
        with open(os.path.join(team_dir, "players.json"), "r", encoding="utf-8") as f:
            players = json.load(f)
        return players

    def read_played_matches(self):
        team_dir = os.path.join(self.club.folder, self.folder)
        with open(os.path.join(team_dir, "played-matches.json"), "r", encoding="utf-8") as f:
            played_matches = json.load(f)
        return played_matches

    def read_not_played_matches(self):
        team_dir = os.path.join(self.club.folder, self.folder)
        with open(os.path.join(team_dir, "not-played-matches.json"), "r", encoding="utf-8") as f:
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
            if self in player.teams:
                if not show_zeros and player.apps == 0:
                    continue
                list.append(player)
        for player in sorted(list, key=lambda player: player.minutes, reverse=True):
            print(player)
        print("="*20)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Team(name={self.name}, folder={self.folder})"


class Match:
    def __init__(self, club, team, matchId, state, dateTime, canDateTimeChange, scores, host, guest, league, play):
        self.club = club
        self.team = team
        self.matchId = matchId
        self.state = state
        self.dateTime = dateTime
        self.canDateTimeChange = canDateTimeChange
        self.scores = scores
        self.host = host
        self.guest = guest
        self.league = league
        self.play = play

        self.events = None

    def load_events(self):
        match_dir = os.path.join(self.club.folder, self.team.folder, self.get_id())
        try:
            with open(os.path.join(match_dir, "events.json"), "r", encoding="utf-8") as f:
                events = json.load(f)
        except FileNotFoundError:
            events = []
        self.events = events

    def prep_stats(self):
        self.load_events()
        if self.host["abbreviation"] == "POL":
            players = self.events["host"]["squad"]
        else:
            players = self.events["guest"]["squad"]

        for player in players:
            p = self.club.get_player(player["id"])
            appearance = Appearance(self.team,
                                    self,
                                    player["type"],
                                    player["number"],
                                    player["isCaptain"],
                                    player["isKeeper"],
                                    player["isJunior"],
                                    player["goals"],
                                    player["cards"],
                                    player["substitutions"])
            p.add_appearance(appearance)

    def __str__(self):
        rpr = "abbreviation"
        if self.state == "Nierozegrany":
            return f"{self.host[rpr]} vs {self.guest[rpr]}"
        return f"{self.host[rpr]} {self.scores["final"]} {self.guest[rpr]}"

    def __repr__(self):
        rpr = "abbreviation"
        return f"Match(Host={self.host[rpr]}, Guest={self.guest[rpr]}, State={self.state})"

    def get_id(self):
        abbr = "abbreviation"
        return self.host[abbr] + self.guest[abbr]

    @property
    def url(self):
        return f"https://laczynaspilka.pl/rozgrywki/mecz/{self.matchId}"


class Player:

    def __init__(self, id, firstname, lastname, isKeeper):
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.isKeepeer = isKeeper

        self.teams = []
        self.apperances = []

    def add_team(self, team):
        self.teams.append(team)

    def add_appearance(self, appearance):
        self.apperances.append(appearance)
        self.apperances = sorted(self.apperances, key=lambda app: app.match.dateTime)

    @property
    def apps(self):
        return len([app for app in self.apperances if app.played])

    @property
    def minutes(self):
        return sum([app.duration for app in self.apperances if app.played])

    def get_inline_apps(self):
        return f"{self.apps} apps | {' | '.join([f"{str(app):<20}" for app in self.apperances])}"

    def __str__(self):
        return f"{self.firstname + ' ' + self.lastname:<25} {self.minutes:<4} min | {self.get_inline_apps()}"


class Appearance:

    def __init__(self, team, match, app_type, number, isCaptain, isKeeper, isJunior, goals, cards, substitutions):
        self.team = team
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
        return f"Appearance({self.team}, {self.match}, {self.app_type}, {self.number}, {self.isCaptain}, {self.isKeeper}, {self.isJunior}, {self.goals}, {self.cards}, {self.substitutions})"


if __name__ == "__main__":
    club = Club("Polonia Warszawa", "polonia")
    club.prep_stats()
    team = club.teams[0]
    team.show_players()