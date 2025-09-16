import os
import json
from .sniffer import Sniffer

def prep_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def catch_and_save_files(url, files, dir, savenames=None):
    sniffer = Sniffer()
    sniffer.driver.get(url)
    for i, file in enumerate(files):
        json_data = sniffer.catch_file(file)
        if json_data is None:
            print(f"Failed to catch {file}")
            print(f"{file} file not saved")
            continue
        savename = savenames[i] if savenames and i < len(savenames) else file
        dump_json(dir, savename, json_data, savename)
        print(f"Saved file {file}")
    sniffer.destroy()

def dump_json(dir, savename, json_data):
    if savename.endswith(".json"): savename = savename[:-5]
    with open(f"{dir}/{savename}.json", 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)