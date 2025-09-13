import os
import json
from .sniffer import Sniffer

def prep_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def catch_and_save_files(url, files, dir, savename=None):
    sniffer = Sniffer()
    sniffer.driver.get(url)
    for file in files:
        json_data = sniffer.catch_file(file)
        if json_data is None:
            print(f"Failed to catch {file}")
            print(f"{file} file not saved")
            continue
        dump_json(dir, file, json_data)
        print(f"Saved file {file}")
    sniffer.destroy()

def dump_json(dir, file, json_data):
    if file.endswith(".json"): file = file[:-5]
    with open(f"{dir}/{file}.json", 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)