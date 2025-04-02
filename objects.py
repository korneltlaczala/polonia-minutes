import os
import json

class Club:
    def __init__(self, name, folder):
        self.name = name
        self.folder = folder
        self.teams = []
        self.load_teams()

    def read_teams(self):
        with open(f"{self.folder}/teams.json", "r", encoding="utf-8") as f:
            teams = json.load(f)
        return teams

    def load_teams(self):
        self.teams = []
        teams = self.read_teams()
        for team in teams:
            self.teams.append(Team(self, team["name"], team["folder"], team["url"]))

    def prep_stats(self):
        team = self.teams[0]
        team.load_played_matches()
        played_matches = team.played_matches
        match = played_matches[2]
        print(match)
        match.prep_stats()

class Team:
    def __init__(self, club, name, folder, url):
        self.club = club
        self.name = name
        self.folder = folder
        self.url = url
        self.not_played_matches = []
        self.played_matches = []

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
        players = self.events["host"]["squad"]
        for player in players:
            if player["type"] != "Substitute":
                continue
            print(player["firstname"], player["lastname"])

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

    def __init__(self, firstname, lastname):
        self.firstname = firstname
        self.lastname = lastname

        self.apperances = []

class Appearance:

    def __init__(self, type, minute_in, minute_out, team, match):
        self.type = type
        self.minute_in = minute_in
        self.minute_out = minute_out
        self.team
        self.match

    @property
    def duration(self):
        return self.minute_out - self.minute_in + 1


if __name__ == "__main__":
    club = Club("Polonia Warszawa", "polonia")
    club.prep_stats()