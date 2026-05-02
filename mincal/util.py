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
        dump_json(dir, savename, json_data)
        print(f"Saved file {file}")
    sniffer.destroy()

def dump_json(dir, savename, json_data):
    if savename.endswith(".json"): savename = savename[:-5]
    with open(f"{dir}/{savename}.json", 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)

def get_json_data(response):
    from seleniumwire.utils import decode
    import json
    body = decode(response.body(), response.headers.get('Content-Encoding', 'identity'))
    body = body.decode('utf-8')
    json_data = json.loads(body)
    return json_data

def catch_and_save_files_playwright(url, files, dir, savenames=None):
    from playwright.sync_api import sync_playwright, Playwright
    import random, time

    saved_files = [False] * len(files)

    def run(playwright: Playwright) -> None:
        prep_dir(dir)
        browser = playwright.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        USER_AGENTS = [
            # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36",          # Ten jest do dupy, działa tylko czasem
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15" # Ten działa chyba zawsze
        ]
        user_agent = random.choice(USER_AGENTS)


        context = browser.new_context(
            user_agent=user_agent,
            viewport={"width": random.randint(1200, 1920), "height": random.randint(700, 1080)},
            locale=random.choice(["en-US", "pl-PL"]),
            timezone_id=random.choice(["Europe/Warsaw", "Europe/Berlin"]),
        )
        page = context.new_page()

        def on_response(response):
            req = response.request
            if req.resource_type != "xhr":
                return
            file_name = req.url.split("/")[-1].split("?")[0]
            if file_name in files:
                savename = savenames[files.index(file_name)] if savenames and file_name in savenames else file_name
                json_data = get_json_data(response)
                dump_json(dir, savename, json_data)
                print(f"\tSaved file {file_name}")
                saved_files[files.index(file_name)] = True
                
        t = 3   # time factor
        page.on("response", on_response)
        time.sleep(random.uniform(t - t/4, t + t/4))
        page.mouse.move(random.randint(0, 800), random.randint(0, 600))
        time.sleep(random.uniform(t/2 - t/4, t/2 + t/4))
        page.goto(
            url,
            wait_until="networkidle"
        )
        browser.close()

        print("Connection closed.")
        # print("user agent:", user_agent)
        if all(saved_files):
            print("✅ All files saved successfully.")
            return
        print("❌ Failed to save files:")
        for i, saved in enumerate(saved_files):
            if not saved:
                print(f" - {files[i]}")

    with sync_playwright() as playwright:
        run(playwright)

