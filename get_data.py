from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle
import json
from datetime import datetime
import os


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=options)
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return driver


def login(driver, username, password):
    driver.get("https://twilight.zalenia.com/")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "usernameField"))
    ).send_keys(username)
    driver.find_element(By.ID, "passwordField").send_keys(password)
    driver.find_element(
        By.XPATH, "/html/body/div/div[2]/div/div[2]/div[2]/div/div/div/div[1]"
    ).click()
    time.sleep(2)


def fetch_data(driver, url):
    driver.get(url)
    data = (
        WebDriverWait(driver, 10)
        .until(EC.presence_of_element_located((By.XPATH, "/html/body/pre")))
        .text
    )
    return json.loads(data)


def save_data(data, folder, prefix):
    current_time = time.strftime("%Y%m%dT%H%M%S")
    filename = f"{folder}/{prefix}{current_time}"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as fp:
        pickle.dump(data, fp)


def get_data():
    driver = setup_driver()
    try:
        login(driver, "1beardedlady", "1beardedlady")

        data_sources = [
            ("https://twilight.zalenia.com/api/world/state", "WorldData", "wdata"),
            ("https://twilight.zalenia.com/api/player/list", "PlayerData", "pdata"),
            ("https://twilight.zalenia.com/api/world/dungeons", "DungeonData", "ddata"),
            ("https://twilight.zalenia.com/api/world/altars", "AltarData", "adata"),
            ("https://twilight.zalenia.com/api/world/bosses", "BossData", "bdata"),
        ]

        save_folder = "D:/ZaleniaData"
        for url, folder, prefix in data_sources:
            data = fetch_data(driver, url)
            save_data(data, f"{save_folder}/{folder}", prefix)
            time.sleep(2)

    finally:
        driver.quit()


def main():
    time_ranges = [
        {"start": "01:55:00", "end": "02:05:00"},
        {"start": "07:55:00", "end": "08:05:00"},
        {"start": "13:55:00", "end": "14:05:00"},
        {"start": "19:55:00", "end": "20:05:00"},
    ]

    while True:
        now = datetime.now().time()
        for tr in time_ranges:
            start = datetime.strptime(tr["start"], "%H:%M:%S").time()
            end = datetime.strptime(tr["end"], "%H:%M:%S").time()
            if start <= now <= end or (start > end and (now >= start or now <= end)):
                print(f"Getting the data at {now}")
                get_data()
                print("Sleeping for 5 hours")
                time.sleep(5 * 60 * 60)
                break
        else:
            print(f"Current time is {now}, waiting 5 minutes.")
            time.sleep(5 * 60)


if __name__ == "__main__":
    main()
