import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import aria2p
import os
import time
import nest_asyncio
import asyncio
import subprocess

# Apply the nest_asyncio patch
nest_asyncio.apply()

# Start aria2c daemon
os.system("nohup aria2c --enable-rpc --rpc-listen-all=true --rpc-allow-origin-all > aria2c.log 2>&1 &")

aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret=""
    )
)


def safe_run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd, output=result.stdout, stderr=result.stderr)
    return result

def add_download(api, uri, out):
    options = {"out": out}
    download = api.add_uris([uri], options=options)
    return download

def get_status(api, gid):
    try:
        download = api.get_download(gid)
        total_length = download.total_length
        completed_length = download.completed_length
        download_speed = download.download_speed
        file_name = download.name
        progress = (completed_length / total_length) * 100 if total_length > 0 else 0
        is_complete = download.is_complete

        return {
            "gid": download.gid,
            "status": download.status,
            "file_name": file_name,
            "total_length": format_bytes(total_length),
            "completed_length": format_bytes(completed_length),
            "download_speed": format_bytes(download_speed),
            "progress": f"{progress:.2f}%",
            "is_complete": is_complete
        }
    except Exception as e:
        print(f"Failed to get status for GID {gid}: {e}")
        raise

def remove_download(api, gid):
    try:
        api.remove([gid])
        print(f"Successfully removed download: {gid}")
    except Exception as e:
        print(f"Failed to remove download: {e}")
        raise

def format_bytes(byte_count):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    index = 0
    while byte_count >= 1024 and index < len(suffixes) - 1:
        byte_count /= 1024
        index += 1
    return f"{byte_count:.2f} {suffixes[index]}"

login_url = 'https://surf.jetmirror.xyz/login'
username = 'jet'
password = 'surf'

login_data = {
    'username': username,
    'password': password
}

base_scrape_url = 'https://surf.jetmirror.xyz/channel/-1002105476348?page={}'

session = requests.Session()

def login(session, login_url, login_data):
    try:
        response = session.post(login_url, data=login_data)
        response.raise_for_status()  # Raise an exception for bad responses

        if response.status_code == 200:
            print("Login successful")
        else:
            print("Login unsuccessful")

    except requests.exceptions.RequestException as e:
        print(f"Error logging in: {e}")

def fetch_and_extract_links(session, url):
    try:
        response = session.get(url)
        response.raise_for_status()  # Raise an exception for bad responses

        soup = BeautifulSoup(response.content, 'html.parser')

        cards = soup.find_all('div', class_='content')

        links_and_subtitles = []
        for card in cards:
            a_tag = card.find('a', href=True)
            if a_tag:
                href = urljoin(url, a_tag['href'])
                subtitle = card.find('p', class_='card-subtitle').text.strip()
                links_and_subtitles.append((href, subtitle))

        return links_and_subtitles

    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return []

login(session, login_url, login_data)

def fetch():
    try_page = 1
    complete_page = False
    all_links_and_subtitles = []
    
    while not complete_page:
        scrape_url = base_scrape_url.format(try_page)
        links_and_subtitles = fetch_and_extract_links(session, scrape_url)
        
        if len(links_and_subtitles) == 0:
            complete_page = True
            break
        
        print(f"Fetching Links from Page {try_page}")
        all_links_and_subtitles.extend(links_and_subtitles)
        
        try_page += 1
    
    return all_links_and_subtitles

async def main():
    print("Bot started")
    links_and_subtitles = fetch()
    for href, subtitle in links_and_subtitles:
      print(href,subtitle)
      if href.startswith("https://surf.jetmirror.xyz/watch/-1002105476348"):
        video_url =  href.replace("watch/","")
        output_file = subtitle.replace("/app/","tb") + ".mp4"  # Assuming the video files are .mp4
        print(f"Downloading {subtitle} from {video_url}")
        
        video = add_download(aria2, video_url, output_file)
        
        while True:
            status = get_status(aria2, video.gid)
            print(status, end="\r")
            time.sleep(2)
            
            if status['is_complete']:
                print(f"Download complete: {status['file_name']}")
                 break

asyncio.get_event_loop().run_until_complete(main())
