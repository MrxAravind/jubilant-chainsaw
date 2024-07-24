import os
from pyrogram import Client, filters
import subprocess


api_id = 21409951
api_hash = "5acdb5491989cb7e4527a3bd61fa112d"
bot_token = "7031135933:AAELXo4tffYkvaxcWsXrmooETXQT777phSQ"
app = Client("Spidy", api_id, api_hash, bot_token=bot_token)


async def run_speedtest():
    # Run the speedtest command and capture the output
    process = await asyncio.create_subprocess_shell(
        'speedtest --format=json',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode == 0:
        return stdout.decode()
    else:
        print(f"Error: {stderr.decode()}")
        return None


async def main():
   async with app:
       speedtest_output = await run_speedtest()
       if speedtest_output:
          print("Speedtest output:", speedtest_output)
          await app.send_message(1039959953,speedtest_output)

  
print("Bot Started")
app.run(main())


