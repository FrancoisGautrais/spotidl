




import os

DB_FILE="db.json"
USER_DIR="user"
WWW_DIR = "www"
PORT=8080
OUTPUT_DIR="out"
OUTPUT_FORMAT="{artist}/{album}/{track-number}-{track-name}.{output-ext}"
FFMPEG="ffmpeg"
try:
    with open("config.cfg") as f:
        exec(f.read())
except:
    pass
