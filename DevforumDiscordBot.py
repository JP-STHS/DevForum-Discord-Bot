import os
import requests
import json
import discord
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1026891262953017455  # replace with your Discord channel ID

# DevForum categories
CATEGORIES = [
    "https://devforum.roblox.com/c/updates/announcements/36.json",
    "https://devforum.roblox.com/c/updates/news-alerts/193.json"
]

SEEN_FILE = "seen.json"

# Load seen topic IDs
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen = set(json.load(f))
else:
    seen = set()

# Fetch topics from a category
def fetch_topics(url):
    data = requests.get(url).json()
    topics = data["topic_list"]["topics"]
    return [(t["id"], t["title"], f"https://devforum.roblox.com/t/{t['slug']}/{t['id']}") for t in topics]

# Collect new posts
new_posts = []
for url in CATEGORIES:
    for tid, title, link in fetch_topics(url):
        if tid not in seen:
            seen.add(tid)
            new_posts.append((title, link))

# Save updated seen topics
with open(SEEN_FILE, "w") as f:
    json.dump(list(seen), f)

# Send to Discord
intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def main():
    await client.login(TOKEN)
    await client.connect()
    
    channel = await client.fetch_channel(CHANNEL_ID)  # fetch the channel via API

    for title, link in reversed(new_posts):
        await channel.send(f"📢 **{title}**\n{link}")
    
    await client.close()

asyncio.run(main())