# ypt1972
import requests
from bs4 import BeautifulSoup
import re
import os
from packaging import version

BASE_URL = "https://download.qemu.org/"
TARGET_FILE = "qemu.tar.xz"
VERSION_TRACKER = "linux.version.txt"


def download_latest_linux_qemu():
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        pattern = re.compile(r'qemu-(\d+\.\d+\.\d+)\.tar\.xz$')

        found_files = []
        for a in soup.find_all('a', href=True):
            clean_href = a['href'].lstrip('/')
            match = pattern.search(clean_href)
            if match:
                found_files.append((match.group(1), clean_href))

        if not found_files:
            print("No files found.")
            return

        found_files.sort(key=lambda x: version.parse(x[0]), reverse=True)
        latest_file = found_files[0][1]

        if os.path.exists(VERSION_TRACKER):
            with open(VERSION_TRACKER, "r") as f:
                current_local_version = f.read().strip()

            if current_local_version == latest_file and os.path.exists(TARGET_FILE):
                print(f"You already have the latest version ({latest_file}). Skipping download.")
                return

        download_url = BASE_URL + latest_file
        print(f"New version found! Downloading: {latest_file}")

        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(TARGET_FILE, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        with open(VERSION_TRACKER, "w") as f:
            f.write(latest_file)

        print(f"Done! Saved as {TARGET_FILE}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    download_latest_linux_qemu()