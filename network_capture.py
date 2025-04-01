import os
import time
from selenium.webdriver.firefox.options import Options
from seleniumwire import webdriver
from seleniumwire.utils import decode
import json

class Sniffer:
    def __init__(self):
        options = Options()
        options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        self.driver = webdriver.Firefox(options=options)
        self.team = None

    def wait_for(self, filename, delay=0.1):
        while not self.file_loaded(filename):
            print(f"Waiting for {filename}...")
            time.sleep(delay)
        print(f"File {filename} found!")

    def file_loaded(self, filename):
        for request in self.driver.requests:
            if f"/{filename}" in request.url and request.response is not None:
                return True
        return False

    def save_file(self, filename):
        self.wait_for(filename)
        for request in self.driver.requests:
            if f"/{filename}" in request.url:
                response = request.response
                body = decode(response.body, response.headers.get('Content-Encoding', 'identity'))
                body = body.decode('utf-8')

                print(f"Response for {filename}:")
                print(f"Status code: {response.status_code}")
                print(f"Headers: {response.headers}")
                print(f"Body preview: {body[:200]}...")  # Print first 200 chars

                json_data = json.loads(body)
                with open(f"files/{self.team.folder}/{filename}.json", 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=4, ensure_ascii=False)

    def capture(self, team):
        self.set_team(team)
        self.validate_team()
        self.prep_dir()
        self.driver.get(self.team.url)
        
        self.save_file("played-matches")
        self.save_file("not-played-matches")
        self.save_file("players")
        with open(f"files/{self.team.folder}/team.json", 'w', encoding='utf-8') as f:
            json.dump(self.team.__dict__, f, indent=4, ensure_ascii=False)

    def validate_team(self):
        if self.team is None:
            raise Exception("Team is not set")
        if self.team.name is None:
            raise Exception("Team name is not set")
        if self.team.folder is None:
            raise Exception("Team folder is not set")
        if self.team.url is None:
            raise Exception("Team url is not set")

    def set_team(self, team):
        self.team = team

    def prep_dir(self):
        if not os.path.exists(f"files/{self.team.folder}/"):
            os.makedirs(f"files/{self.team.folder}/")

    def destroy(self):
        self.driver.quit()

if __name__ == "__main__":
    sniffer = Sniffer()
    # sniffer.capture("Polonia B2", "https://www.laczynaspilka.pl/rozgrywki/druzyna/c8b159df-2099-40d4-885e-a6168d643519")
