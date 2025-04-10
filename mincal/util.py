import os
import json
from .sniffer import Sniffer

def prep_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def catch_and_save_files(url, files, dir):
    sniffer = Sniffer()
    sniffer.driver.get(url)
    for file in files:
        json_data = sniffer.catch_file(file)
        dump_json(dir, file, json_data)
    sniffer.destroy()

def dump_json(dir, file, json_data):
    with open(f"{dir}/{file}.json", 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)