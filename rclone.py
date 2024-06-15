import os
os.system("apt install rclone")
os.system("wget https://gist.github.com/MrxAravind/cff83e9fa0d8b3f627e4d049c893b776/raw/3eec18861e0635b54ad50191c0fea91b5f339e86/rclone.conf")
os.system("rclone --config rclone.conf serve webdav --addr :8080")
