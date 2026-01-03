# ypt1972
import requests
from bs4 import BeautifulSoup
import re
import os

BASE_URL = "https://qemu.weilnetz.de/w64/"
TARGET_FILE = "qemu.exe"
VERSION_TRACKER = "windows.version.txt"


def download_latest_qemu():
    print(f"Checking for updates at {BASE_URL}...")

    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        pattern = re.compile(r'qemu-w64-setup-(\d{8})\.exe')

        links = []
        for a in soup.find_all('a', href=True):
            clean_href = a['href'].lstrip('/')
            match = pattern.search(clean_href)
            if match:
                links.append((match.group(1), clean_href))

        if not links:
            print("Could not find any installers on the page.")
            return

        links.sort(key=lambda x: x[0], reverse=True)
        latest_file = links[0][1]

        if os.path.exists(VERSION_TRACKER):
            with open(VERSION_TRACKER, "r") as f:
                current_local_version = f.read().strip()

            if current_local_version == latest_file and os.path.exists(TARGET_FILE):
                print(f"You already have the latest version ({latest_file}). Skipping download.")
                return

        full_download_url = BASE_URL + latest_file
        print(f"New version found: {latest_file}")
        print(f"Downloading and saving as: {TARGET_FILE}...")

        with requests.get(full_download_url, stream=True) as r:
            r.raise_for_status()
            with open(TARGET_FILE, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        with open(VERSION_TRACKER, "w") as f:
            f.write(latest_file)

        print("Success! The file has been downloaded and tracker updated.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    download_latest_qemu()