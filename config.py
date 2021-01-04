




import os

DB_FILE="db.json"
USER_DIR="user"
WWW_DIR = "www"

OUTPUT_DIR="out"
OUTPUT_FORMAT="{artist}/{album}/{track-number}-{track-name}.{output-ext}"

try:
    with open("config.cfg") as f:
        exec(f.read())
except:
    pass
