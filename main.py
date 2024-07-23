import time
import aria2p
import requests
import os
from pyrogram import Client, filters
from datetime import datetime
import asyncio

# Start aria2c in the background
os.system("nohup aria2c --enable-rpc --rpc-listen-all=true --rpc-allow-origin-all > aria2c.log 2>&1 &")

# Initialize aria2p API client
aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret=""
    )
)

# Initialize the Telegram bot client
api_id = 21409951
api_hash = "5acdb5491989cb7e4527a3bd61fa112d"
bot_token = "7031135933:AAELXo4tffYkvaxcWsXrmooETXQT777phSQ"
app = Client("Spidy", api_id, api_hash, bot_token=bot_token)

up = {}


def add_download(api, uri):
    download = api.add_uris([uri])
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

async def progress(current, total, status, filename, start,timer):
    current_time = time.time()
    diff = current_time - start
    if round(diff % 5.00) == 0 or current == total:
        uploaded = current
        percentage = (current / total) * 100
        elapsed_time_seconds = (datetime.now() - timer).total_seconds()
        progress_text = format_progress_bar(
                filename=filename,
                percentage=percentage,
                done=current,
                total_size=total,
                status="Uploading",
                eta=(total - current) / (current / elapsed_time_seconds) if current > 0 else 0,
                speed=current / elapsed_time_seconds if current > 0 else 0,
                elapsed=elapsed_time_seconds,
                aria2p_gid=""
            )
        await status.edit_text(progress_text)

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


def format_progress_bar(filename, percentage, done, total_size, status, eta, speed, elapsed, aria2p_gid):
    bar_length = 10
    filled_length = int(bar_length * percentage / 100)
    bar = '★' * filled_length + '☆' * (bar_length - filled_length)
    def format_size(size):
        size = int(size)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size / 1024:.2f} KB"
        elif size < 1024 ** 3:
            return f"{size / 1024 ** 2:.2f} MB"
        else:
            return f"{size / 1024 ** 3:.2f} GB"
    
    def format_time(seconds):
        seconds = int(seconds)
        if seconds < 60:
            return f"{seconds} sec"
        elif seconds < 3600:
            return f"{seconds // 60} min"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours} hr {minutes} min"
    
    return (
        f"┏ ғɪʟᴇɴᴀᴍᴇ: {filename}\n"
        f"┠ [{bar}] {percentage:.2f}%\n"
        f"┠ ᴘʀᴏᴄᴇssᴇᴅ: {format_size(done)} ᴏғ {format_size(total_size)}\n"
        f"┠ sᴛᴀᴛᴜs: {status}\n"
        f"┠ sᴘᴇᴇᴅ: {format_size(speed)}/s"
        )

@app.on_message(filters.private & filters.text)
async def terabox(client, message):
    if message.text.startswith("https://"):
        query = message.text
        url = f"https://teraboxvideodownloader.nepcoderdevs.workers.dev/?url={query}"
        try:
            status = await message.reply_text(f"Processing Link")
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                resolutions = data["response"][0]["resolutions"]
                fast_download_link = resolutions["Fast Download"]
                hd_video_link = resolutions["HD Video"]
                thumbnail_url = data["response"][0]["thumbnail"]
                video_title = data["response"][0]["title"]
                download = add_download(aria2, fast_download_link)
                video  = api.get_download(download.gid)
                start_time = datetime.now()
                retry_error = 1
                status = await status.edit_text(f"Downloading {video_title}")
                while not video.is_complete:
                    video.update()
                    print(video)
                    percentage = video.progress
                    done = video.completed_length
                    total_size = video.total_length
                    speed = video.download_speed
                    eta = video.eta
                    elapsed_time_seconds = (datetime.now() - start_time).total_seconds()
                    progress_text = format_progress_bar(
                          filename=video_title,
                          percentage=percentage,
                          done=done,
                          total_size=total_size,
                          status="Downloading",
                          eta=eta,
                          speed=speed,
                          elapsed=elapsed_time_seconds,
                          aria2p_gid=video.gid
                             )
                    if status.text != progress_text:
                         status = await status.edit_text(text=progress_text)
                    await asyncio.sleep(2)
                    
                    if video.is_complete:
                        file_path = download.files[0].path

                        thumbnail_path = "thumbnail.jpg"
                        thumbnail_response = requests.get(thumbnail_url)
                        with open(thumbnail_path, "wb") as thumb_file:
                             thumb_file.write(thumbnail_response.content)

                        
                        print("Download complete!")
                        start_time = time.time()
                        start_time2 = datetime.now()
                        with open(file_path, 'rb') as file:
                           await app.send_video(chat_id=message.chat.id, video=file, thumb=thumbnail_path,progress=progress, progress_args=(status,file_path,start_time,start_time2))
                        await asyncio.sleep(1)
                        await status.delete()
                        os.remove(file_path)
                        os.remove(thumbnail_path)
                        break
                    time.sleep(2)

            else:
                await app.send_message(chat_id=message.chat.id, text="Failed To Fetch the Link")
        except Exception as e:
            print(e)
            await app.send_message(chat_id=message.chat.id, text=str(e))
    else:
        await app.send_message(chat_id=message.chat.id, text="Send a valid URL")

print("Bot Started")
app.run()
