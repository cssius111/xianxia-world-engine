import os
import pathlib
import threading
import time

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def run_app():
    ROOT = pathlib.Path(__file__).resolve().parents[1]
    os.chdir(ROOT)
    import sys

    sys.path.insert(0, str(ROOT))
    from run_web_ui_v2 import XianxiaWebServer

    server = XianxiaWebServer()
    server.app.run(port=5001)


def main():
    t = threading.Thread(target=run_app, daemon=True)
    t.start()
    time.sleep(5)
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    urls = [
        "http://localhost:5001/start",
        "http://localhost:5001/choose",
        "http://localhost:5001/roll",
        "http://localhost:5001/game",
    ]
    for url in urls:
        driver.get(url)
        r = requests.get(url)
        assert r.status_code == 200
    driver.quit()
    print("Smoke UI check passed")


if __name__ == "__main__":
    main()
