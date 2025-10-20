import asyncio
import json
import os
from datetime import datetime, timezone

import discord


TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = os.getenv("DISCORD_WIDGET_GUILD_ID") or os.getenv("DISCORD_GUILD_ID")
TARGET_USER_ID = os.getenv("DISCORD_PRESENCE_USER_ID") or os.getenv("DISCORD_OWNER_ID")
PRESENCE_FILE = os.getenv("DISCORD_PRESENCE_FILE", "runtime/presence.json")


intents = discord.Intents.default()
intents.presences = True
intents.members = True

client = discord.Client(intents=intents)


def write_presence(status: str):
    if not TARGET_USER_ID:
        return
    data = {
        "user_id": str(TARGET_USER_ID),
        "status": status,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    os.makedirs(os.path.dirname(PRESENCE_FILE), exist_ok=True)
    with open(PRESENCE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


@client.event
async def on_ready():
    # Try initial fetch
    try:
        if GUILD_ID and TARGET_USER_ID:
            guild = client.get_guild(int(GUILD_ID))
            if guild is None:
                guild = await client.fetch_guild(int(GUILD_ID))
            member = guild.get_member(int(TARGET_USER_ID))
            if member is None:
                # Ensure member cache by fetching
                member = await guild.fetch_member(int(TARGET_USER_ID))
            status = str(getattr(member, "status", "offline"))
            write_presence(status)
    except Exception:
        # Ignore startup issues
        pass


@client.event
async def on_presence_update(before: discord.Member, after: discord.Member):
    try:
        if TARGET_USER_ID and str(after.id) == str(TARGET_USER_ID):
            status = str(getattr(after, "status", "offline"))
            write_presence(status)
    except Exception:
        pass


def main():
    if not TOKEN:
        print("Missing DISCORD_BOT_TOKEN; bot not starting")
        return
    client.run(TOKEN)


if __name__ == "__main__":
    main()

