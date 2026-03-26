import discord
from discord.ext import commands, tasks
import requests
import logging
from dotenv import load_dotenv
import os
import json

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

CHANNEL_ID = 1026891262953017455  # replace with your channel ID

ANNOUNCEMENTS_URL = "https://devforum.roblox.com/c/updates/announcements/36.json"
NEWS_URL = "https://devforum.roblox.com/c/updates/news-alerts/193.json"

SEEN_FILE = "seen_topics.json"

handler = logging.FileHandler(
    filename="discord.log",
    encoding="utf-8",
    mode="w"
)

intents = discord.Intents.default()
bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# Load seen topics
def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

seen_topics = load_seen()


def get_topics(url):
    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to fetch:", url)
        return []

    data = response.json()

    topics = data["topic_list"]["topics"]

    results = []

    for topic in topics:
        topic_id = topic["id"]
        title = topic["title"]
        slug = topic["slug"]

        link = f"https://devforum.roblox.com/t/{slug}/{topic_id}"

        results.append((topic_id, title, link))

    return results


@tasks.loop(seconds=60)
async def check_for_updates():

    await bot.wait_until_ready()

    channel = bot.get_channel(CHANNEL_ID)

    urls = [
        ANNOUNCEMENTS_URL,
        NEWS_URL
    ]

    new_posts = []

    for url in urls:
        topics = get_topics(url)

        for topic_id, title, link in topics:

            if topic_id not in seen_topics:

                seen_topics.add(topic_id)

                new_posts.append((title, link))

    if new_posts:

        save_seen(seen_topics)

        for title, link in reversed(new_posts):

            message = f"📢 **New DevForum Post**\n{title}\n{link}"

            await channel.send(message)


@bot.event
async def on_ready():

    print("Bot is online")

    check_for_updates.start()


bot.run(TOKEN, log_handler=handler)