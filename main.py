import time
import asyncio
from techzdl import TechZDL
import requests
import os
from pyrogram import Client, filters
from datetime import datetime

api_id = 21409951
api_hash = "5acdb5491989cb7e4527a3bd61fa112d"
bot_token = "7031135933:AAELXo4tffYkvaxcWsXrmooETXQT777phSQ"
app = Client("Spidy", api_id, api_hash, bot_token=bot_token)

up = {}



async def progress(current, total,status,start):
     current_time = time.time()
     diff = current_time - start
     if round(diff % 5.00) == 0 or current == total:
         per = f"{current * 100 / total:.1f}%"
         start_time = current_time
         await status.edit_text(f"{status.text}\nStatus:Uploading\nProgress:{format_bytes(current)} / {format_bytes(total)} [{per}]")
        
def format_bytes(byte_count):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    index = 0
    while byte_count >= 1024 and index < len(suffixes) - 1:
        byte_count /= 1024
        index += 1
    return f"{byte_count:.2f} {suffixes[index]}"

async def progress_callback(description, done, total,status,uploadedeps):
    await status.edit_text(f"{status.text}\nDownloaded Eps:{uploadedeps}\nStatus:Downloading\nDLProgress:{format_bytes(done)} / {format_bytes(total)}")
    

@app.on_message(filters.private & filters.text)
async def terabox(client, message):
    if message.text.startswith("https://"):
        query = message.text
        url = f"https://teraboxvideodownloader.nepcoderdevs.workers.dev/?url={query}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                resolutions = data["response"][0]["resolutions"]
                fast_download_link = resolutions["Fast Download"]
                hd_video_link = resolutions["HD Video"]
                thumbnail_url = data["response"][0]["thumbnail"]
                video_title = f"{data["response"][0]["title"]}.mp4"
                status = await message.reply_text(f"Downloading: {video_title}")
                img_downloader = TechZDL(url=thumbnail_url)
                vid_downloader = TechZDL(url=fast_download_link,
                              filename=video_title,
                              debug=False,
                              progress=False,
                              progress_callback=progress_callback,
                              progress_args=(status,),
                              progress_interval=3,)
                await img_downloader.start()
                await vid_downloader.start()
                img_info = await img_downloader.get_file_info()     
                file_info = await vid_downloader.get_file_info()
                print("Starting To Upload..")
                start_time = time.time()
                status = await pmsg.edit_text(message.chat.id, f"Uploading: {video_title}")
                await app.send_video(chat_id=message.chat.id, video="downloads/"+file_info['filename'], thumb="downloads/"+img_info['filename'],progress=progress, progress_args=(status,))
                await reply.delete()
                os.remove("downloads/"+file_info['filename'])
                os.remove("downloads/"+img_info['filename'])

            else:
                await app.send_message(chat_id=message.chat.id, text="Failed To Fetch the Link")
        except Exception as e:
            await app.send_message(chat_id=message.chat.id, text=str(e))
    else:
        await app.send_message(chat_id=message.chat.id, text="Send a valid URL")

print("Bot Started")
app.run()
