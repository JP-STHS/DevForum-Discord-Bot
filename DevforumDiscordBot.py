import discord
import asyncio
import json
import os
import aiohttp

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1486815317307953366  # replace with your Discord channel ID

SEEN_FILE = "seen_topics.json"

# DevForum categories to track
CATEGORIES = [
    "https://devforum.roblox.com/c/updates/announcements/36.json",
    "https://devforum.roblox.com/c/updates/news-alerts/193.json"
]

intents = discord.Intents.default()
client = discord.Client(intents=intents)


async def fetch_new_topics():
    """Fetch latest topics and return new ones not in seen_topics.json"""
    seen = set()
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            seen = set(json.load(f))

    new_posts = []

    async with aiohttp.ClientSession() as session:
        for url in CATEGORIES:
            async with session.get(url) as resp:
                data = await resp.json()
                for topic in data.get("topic_list", {}).get("topics", []):
                    tid = topic.get("id")
                    title = topic.get("title")
                    link = f"https://devforum.roblox.com/t/{tid}"
                    if tid not in seen:
                        new_posts.append((title, link))
                        seen.add(tid)

    # save updated seen list
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

    return new_posts


async def main():
    if not TOKEN:
        raise ValueError("DISCORD_TOKEN not set")

    await client.login(TOKEN)
    await client.connect()

    # Fetch channel via API to avoid None
    try:
        channel = await client.fetch_channel(CHANNEL_ID)
    except discord.Forbidden:
        print("Bot does not have permission to access the channel")
        await client.close()
        return
    except discord.NotFound:
        print("Channel not found")
        await client.close()
        return

    new_posts = await fetch_new_topics()

    for title, link in reversed(new_posts):
        try:
            await channel.send(f"📢 **{title}**\n{link}")
        except discord.Forbidden:
            print(f"Cannot send message to channel {CHANNEL_ID}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())