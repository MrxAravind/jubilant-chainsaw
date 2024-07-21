import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import time
import asyncio
import subprocess
from techzdl import TechZDL
from swibots import BotApp

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTAyMDUsImlzX2JvdCI6dHJ1ZSwiYWN0aXZlIjp0cnVlLCJpYXQiOjE3MTM2MTQxOTgsImV4cCI6MjM0NDc2NjE5OH0.-SHFOkXWreqsjTjcM5V7GLaTZwfW62DGlzeGoYuQSnY"
bot = BotApp(TOKEN)




async def upload_progress_handler(progress):
    print(f"Upload progress: {format_bytes(progress.readed+progress.current)}")


async def switch_upload(file):
    file = f"download/{file}"
    res = await bot.send_media(
        message=f"{os.path.basename(file)}",
        community_id="10fccf16-fe33-4139-8554-c493abd33a42",
        group_id="bd1d170a-bcb5-4ac1-9314-3c9b16ac4354",
        document=file,
        part_size=50*1024*1024,
        task_count=20,
        progress= upload_progress_handler)
    return res



def safe_run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd, output=result.stdout, stderr=result.stderr)
    return result

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


def progress_callback(description, done, total):
    print(f"{description}: {format_bytes(done)}/{format_bytes(total)} MB downloaded")


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
        
        if len(links_and_subtitles) == 0 or try_page == 10:
            complete_page = True
            break
        
        print(f"Fetching Links from Page {try_page}")
        all_links_and_subtitles.extend(links_and_subtitles)
        
        try_page += 1
    
    return all_links_and_subtitles

async def main():
    links_and_subtitles = fetch()
    for href, subtitle in links_and_subtitles:
      if href.startswith("https://surf.jetmirror.xyz/watch/-1002105476348"):
              video_url =  href.replace("watch/","")
              downloader = TechZDL(
                              url=video_url,
                              debug=False,
                              progress=False,
                              progress_callback=progress_callback,
                              progress_interval=2,)
              await downloader.start()
              file_info = await downloader.get_file_info()
              print(f"Filename: {file_info['filename']}")
              if downloader.download_success:
                  print("Download Successful...")
                  print("Starting To Upload..")
                  await switch_upload(file_info['filename'],)
  
asyncio.run(main())
