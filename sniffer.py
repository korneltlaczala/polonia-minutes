import os
import time
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.firefox.options import Options
from seleniumwire import webdriver
from seleniumwire.utils import decode
import json

class Sniffer:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        options = Options()
        # options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)

    def wait_for(self, filename, delay=0.1):
        while not self.file_loaded(filename):
            print(f"Waiting for {filename}...")
            time.sleep(delay)
        print(f"File {filename} found!")

    def file_loaded(self, filename):
        for request in self.driver.requests:
            if f"/{filename}" in request.url and request.response is not None and request.response.status_code == 200:
                return True
        return False

    def catch_file(self, filename):
        self.wait_for(filename)
        for request in self.driver.requests:
            if f"/{filename}" in request.url and request.response is not None and request.response.status_code == 200:
                response = request.response
                body = decode(response.body, response.headers.get('Content-Encoding', 'identity'))
                body = body.decode('utf-8')

                json_data = json.loads(body)
                return json_data

    def capture(self, team):
        self.set_team(team)
        self.validate_team()
        self.prep_dir()
        self.driver.get(self.team.url)
        
        self.save_file("players")
        self.save_file("played-matches")
        self.save_file("not-played-matches")
        with open(f"{self.base_dir}/{self.team.folder}/team.json", 'w', encoding='utf-8') as f:
            json.dump(self.team.__dict__, f, indent=4, ensure_ascii=False)


    def destroy(self):
        self.driver.quit()

if __name__ == "__main__":
    sniffer = Sniffer()
    # sniffer.capture("Polonia B2", "https://www.laczynaspilka.pl/rozgrywki/druzyna/c8b159df-2099-40d4-885e-a6168d643519")
