import requests
from decouple import config

DISCORD_BOT_TOKEN = config("DISCORD_BOT_TOKEN", None)


class DiscordUtils:
    @staticmethod
    def send_message(discord_id, message):
        url = "https://discord.com/api/v10/channels/{discord_id}/messages".format(
            discord_id=discord_id
        )
        headers = {
            "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
            "Content-Type": "application/json",
        }
        data = {"content": message}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            return data.get("id")
        else:
            print("Discord Response:", response.text)
            return None
