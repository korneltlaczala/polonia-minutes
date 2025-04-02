import os
from sniffer import Sniffer
from objects import *
import json

class API:
    def __init__(self, club):
        self.club = club

    def update_matches(self):
        for team in self.club.teams:
            self.update_team_matches(team)

    def update_players(self):
        for team in self.club.teams:
            self.update_team_players(team)

    def update_match_data(self):
        for team in self.club.teams:
            self.update_team_match_data(team)

    def update_team_matches(self, team):
        self.validate_team(team)
        team_dir = os.path.join(self.club.folder, team.folder)
        self.prep_dir(team_dir)
        self.catch_save_files(team.url, ["played-matches", "not-played-matches"], team_dir)

    def update_team_players(self, team):
        self.validate_team(team)
        team_dir = os.path.join(self.club.folder, team.folder)
        self.prep_dir(team_dir)
        self.catch_save_files(team.url, ["players"], team_dir)

    def update_team_match_data(self, team):
        self.read_matches(team)
        self.prep_match_dirs(team)
        self.process_matches(team)

    def prep_match_dirs(self, team):
        team_dir = os.path.join(self.club.folder, team.folder)
        for match in team.played_matches:
            match_dir = os.path.join(team_dir, match.get_id())
            self.prep_dir(match_dir)

    def process_matches(self, team):
        for match in team.played_matches:
            self.process_match(team, match)

    def process_match(self, team, match):
        print("="*20)
        print(f"Processing {match}")
        print(f"match url: {match.url}")
        print("="*20)
        match_dir = os.path.join(self.club.folder, team.folder, match.get_id())
        self.catch_save_files(match.url, ["events"], match_dir)

    def catch_save_files(self, url, files, save_dir):
        sniffer = Sniffer()
        sniffer.driver.get(url)
        for file in files:
            json_data = sniffer.catch_file(file)
            self.dump_json(save_dir, file, json_data)
        sniffer.destroy()

    def dump_json(self, save_dir, file, json_data):
        with open(f"{save_dir}/{file}.json", 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)

    def validate_team(self, team):
        if team is None:
            raise Exception("Team is not set")
        if team.name is None:
            raise Exception("Team name is not set")
        if team.folder is None:
            raise Exception("Team folder is not set")
        if team.url is None:
            raise Exception("Team url is not set")
    
    def prep_dir(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

if __name__ == "__main__":
    club = Club("Polonia Warszawa", "polonia")

    # api = API(club)
    # api.club.load_teams()
    # api.update_matches()
    # api.update_players()
    # api.update_match_data()

    club.prep_stats()
