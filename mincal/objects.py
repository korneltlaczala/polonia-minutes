import pandas as pd
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
                print("Prepping stats for league:", league, " | ", league.id)
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

    def download_matches(self, only_new_leagues=False):
        for league in self.leagues:
            league.download_matches(only_new_leagues=only_new_leagues)

    def download_players(self, force=False):
        for league in self.leagues:
            league.download_players(force=force)

    def download_match_data(self):
        for league in self.leagues:
            league.download_match_data()

    def repair_matches(self):
        for league in self.leagues:
            league.repair_matches()

    def get_players_for_team(self, team_id, active_leagues=None):
        self.folder = self.folder[(self.folder.rfind("/") + 1):]
        team_id = int(team_id)

        if active_leagues is None or len(active_leagues) == 0:
            tempTeam = self.get_team(team_id)
            active_leagues = [league.id for league in tempTeam.active_leagues]

        tempClub = Club(self.name, self.folder)
        tempClub.prep_stats(active_leagues=active_leagues)
        team = tempClub.get_team(team_id)
        players = []
        for player in tempClub.players:
            if player.belongs_to_team(team):
                players.append(player)

        # for player in players:
        #     print(f"{player}")
        #     for app in player.appearances:
        #         print(f"\t{app.match} ({app.duration} min), {app.goals} - {app.goal_count}")

        # print(f"{len(players)} have scored {sum([p.goal_count for p in players])} goals")

        played_matches = team.matches[0]
        for match in played_matches:
            print(f"Match: {match}")
            for player in players:
                for appearance in player.appearances:
                    if appearance.match != match:
                        continue
                    if appearance.goal_count > 0:
                        print(f"\t{player} scored {appearance.goal_count} goals")
                        
        return players

    def get_matches_for_team(self, team_id, active_leagues=None):
        self.folder = self.folder[(self.folder.rfind("/") + 1):]
        tempClub = Club(self.name, self.folder)
        tempClub.prep_stats(active_leagues=active_leagues)
        team_id = int(team_id)
        team = tempClub.get_team(team_id)
        return team.matches

    def get_appearances_for_player(self, player_id, active_leagues=None):
        self.folder = self.folder[(self.folder.rfind("/") + 1):]
        player_id = str(player_id)

        if active_leagues is None or len(active_leagues) == 0:
            player = self.get_player(player_id)
            if player is None:
                return []
            active_leagues = [league.id for league in player.leagues]

        tempClub = Club(self.name, self.folder)
        tempClub.prep_stats(active_leagues=active_leagues)
        player = tempClub.get_player(player_id)
        if player is None:
            return []
        return player.appearances

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
    def matches(self):
        played_matches = []
        not_played_matches = []
        for league in self.active_leagues:
            played_matches += league.played_matches
            not_played_matches += league.not_played_matches
        return played_matches, not_played_matches

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
        try:
            return int(self.category_age[2:])
        except:
            return 100

    @property
    def birthyear(self):
        if self.age == 100:
            return "seniorzy"
        if datetime.date.today().month < 7:
            return datetime.date.today().year - self.age
        else:
            return datetime.date.today().year - self.age + 1

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

    def download_matches(self, only_new_leagues=False):
        if only_new_leagues and (self.played_matches_downloaded() and self.not_played_matches_downloaded()):
            print(f"="*60)
            print(f"Matches already downloaded for {self}")
            print(f"="*60)
            return

        dir = os.path.join(self.club.folder, self.folder)
        util.prep_dir(dir)
        print(f"="*60)
        print(f"Downloading matches for {self}...")
        print(f"from {self.url}")
        # print(f"="*60)
        # util.catch_and_save_files(self.url, ["played-matches", "not-played-matches"], dir)
        util.catch_and_save_files_playwright(self.url, ["played-matches", "not-played-matches"], dir)
        self.repair_matches()

    def download_players(self, force=False):
        print(f"="*60)
        if self.players_downloaded() and not force:
            print(f"Players already downloaded for {self}")
            return

        dir = os.path.join(self.club.folder, self.folder)
        util.prep_dir(dir)
        print(f"Downloading players for {self}...")
        print(f"from {self.url}")
        # util.catch_and_save_files(self.url, ["players"], dir)
        util.catch_and_save_files_playwright(self.url, ["players"], dir)

    def download_match_data(self, force=False):
        self.load_matches()
        print(f"="*60)
        print(f"Fetching match data for league {self}...")
        print(f"="*60)
        for match in self.played_matches:
            if match.download_needed() or force:
                match.download_events()
            else: 
                print(f"Results for {match} already downloaded\t file size: {match.events_file_size} bytes")
            # if not match.info_downloaded() or force:
            #     print(f"Downloading info for {match}")
            #     match.download_info()

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

    def played_matches_downloaded(self):
        dir = os.path.join(self.club.folder, self.folder)
        return os.path.exists(os.path.join(dir, "played-matches.json"))
    
    def not_played_matches_downloaded(self):
        dir = os.path.join(self.club.folder, self.folder)
        return os.path.exists(os.path.join(dir, "not-played-matches.json"))

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
        self.duration = None

    def events_downloaded(self):
        match_dir = os.path.join(self.club.folder, self.league.folder, self.id)
        return os.path.exists(os.path.join(match_dir, "events.json"))

    @property
    def events_file_size(self):
        match_dir = os.path.join(self.club.folder, self.league.folder, self.id)
        if not self.events_downloaded():
            return 0
        return os.path.getsize(os.path.join(match_dir, "events.json"))

    def download_needed(self):
        return self.events_file_size < 5000

    def load_events(self):
        match_dir = os.path.join(self.club.folder, self.league.folder, self.id)
        with open(os.path.join(match_dir, "events.json"), "r", encoding="utf-8") as f:
            self.events = json.load(f)

    def is_home_match(self):
        return self.host["abbreviation"] == "POL"

    def prep_stats(self):
        if not self.events_downloaded():
            return

        self.load_events()

        self.duration = 90
        for child in self.events["events"]:
            if child["header"] == "Dogrywka":
                self.duration = 120

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
        # util.catch_and_save_files(self.url, ["events"], match_dir)
        util.catch_and_save_files_playwright(self.url, ["events"], match_dir)

    def download_info(self):
        print(f"Downloading info for {self}")
        print(f"from {self.url}")
        print(f"Match ID: {self.matchId}")
        match_dir = os.path.join(self.club.folder, self.league.folder, self.id)
        util.prep_dir(match_dir)
        # util.catch_and_save_files(self.url, [self.matchId], match_dir, savenames=["info"])
        util.catch_and_save_files_playwright(self.url, [self.matchId], match_dir, savenames=["info"])

    def info_downloaded(self):
        match_dir = os.path.join(self.club.folder, self.league.folder, self.id)
        return os.path.exists(os.path.join(match_dir, "info.json"))

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
    def minutes_per_game(self):
        if self.apps > 0:
            return round(self.minutes / self.apps, 2)
        return 0

    @property
    def goal_count(self):
        return sum([app.goal_count for app in self.appearances])

    @property
    def goals_per_90(self):
        if self.minutes > 0:
            return round(self.goal_count / (self.minutes / 90), 2)
        return 0

    @property
    def goals_per_game(self):
        if self.apps > 0:
            return round(self.goal_count / self.apps, 2)
        return 0

    @property
    def yellow_cards(self):
        return sum([app.yellow_card_count for app in self.appearances])
        
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

    def get_leagues(self):
        """Zwraca listę unikalnych nazw lig, w których zawodnik ma jakiekolwiek występy/powołania."""
        return list(set(app.match.league for app in self.appearances))

    def minutes_by_league(self, league_name):
        """Zwraca sumę minut rozegranych przez zawodnika w konkretnej lidze."""
        return sum([app.duration for app in self.appearances if app.played and app.match.league == league_name])

    def apps_by_league(self, league_name):
        """Zwraca liczbę rozegranych meczów (apps) w konkretnej lidze."""
        return len([app for app in self.appearances if app.played and app.match.league == league_name])

    def callings_by_league(self, league_name):
        """Zwraca liczbę powołań (w kadrze meczowej) w konkretnej lidze."""
        return len([app for app in self.appearances if app.match.league == league_name])

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
        match_duration = self.match.duration if self.match.duration is not None else 90
        self.minute_in = 1
        self.minute_out = match_duration
        

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
            self.minute_in = match_duration+1

    @property
    def goal_count(self):
        if len(self.goals) == 0:
            return 0
        return len(self.goals)

    @property
    def yellow_card_count(self):
        if len(self.cards) == 0:
            return 0
        return len([card for card in self.cards if card["type"].lower() == "yellow" or card["type"].lower() == "secondyellow"])

    @property
    def duration(self):
        if self.played == False:
            return 0
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