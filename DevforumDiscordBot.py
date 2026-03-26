import discord
import os
import requests
import json
from datetime import datetime

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1026891262953017455  # your channel

ANNOUNCEMENTS_URL = "https://devforum.roblox.com/c/updates/announcements/36.json"
NEWS_URL = "https://devforum.roblox.com/c/updates/news-alerts/193.json"

SEEN_FILE = "seen.json"

def load_seen():
    if os.path.exists(SEEN_FILE):
        return set(json.load(open(SEEN_FILE)))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

seen = load_seen()

def get_topics(url):
    res = requests.get(url).json()["topic_list"]["topics"]
    return [(t["id"], t["title"], f"https://devforum.roblox.com/t/{t['slug']}/{t['id']}") for t in res]

# gather all new
new_posts = []
for url in [ANNOUNCEMENTS_URL, NEWS_URL]:
    for tid, title, link in get_topics(url):
        if tid not in seen:
            seen.add(tid)
            new_posts.append((title, link))

save_seen(seen)

# now post to Discord
import discord

client = discord.Client(intents=discord.Intents.default())

async def post():
    await client.login(TOKEN)
    channel = client.get_channel(CHANNEL_ID)
    for title, link in reversed(new_posts):
        await channel.send(f"📢 **{title}**\n{link}")
    await client.close()

import asyncio
asyncio.run(post())