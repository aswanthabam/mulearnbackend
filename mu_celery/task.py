from celery import shared_task
from db.task import TaskList
from utils.discord import DiscordUtils
from utils.utils import send_template_mail
import requests
from decouple import config
from db.user import User

DISCORD_BOT_TOKEN = config("DISCORD_BOT_TOKEN", None)
DISCORD_GUILD_ID = config("DISCORD_GUILD_ID", None)


@shared_task
def send_email(context: dict, subject: str, address: list[str], attachment: str = None):
    return send_template_mail(context, subject, address, attachment)


@shared_task
def send_task_announcement_message(task_id):
    DISCORD_BOT_TOKEN = config("DISCORD_BOT_TOKEN", None)
    if not DISCORD_BOT_TOKEN:
        return {"status": "error", "message": "Discord bot token not set"}
    task = TaskList.objects.select_related("announcement_channel").get(id=task_id)
    if not task.announcement_channel or not task.long_description:
        return {
            "status": "error",
            "message": "Announcement channel or long description not set",
        }
    discord_id = task.announcement_channel.discord_id
    message = task.long_description
    message_id = DiscordUtils.send_message(discord_id, message)
    if not message_id:
        return {"status": "error", "message": "Failed to send message"}
    task.announcement_message_id = message_id
    task.save()


@shared_task
def onboard_user(access_token: str, user_id: int):
    if not DISCORD_BOT_TOKEN or not DISCORD_GUILD_ID:
        return {"status": "error", "message": "Discord bot token or guild id not set"}
    user = User.objects.get(id=user_id)
    user_response = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if user_response.status_code != 200:
        return {"status": "error", "message": "Failed to get user data"}
    user_data = user_response.json()
    discord_user_id = user_data.get("id")
    guild_url = (
        f"https://discord.com/api/guilds/{DISCORD_GUILD_ID}/members/{discord_user_id}"
    )
    member_data = {"access_token": access_token}
    bot_headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json",
    }
    already_linked_account = User.objects.filter(discord_id=discord_user_id).first()
    if already_linked_account:
        already_linked_account.exist_in_guild = False
        already_linked_account.discord_id = None
        already_linked_account.save()
    user.discord_id = discord_user_id
    user.exist_in_guild = True
    user.save()
    join_response = requests.put(guild_url, json=member_data, headers=bot_headers)
    if (
        join_response.status_code != 201
        and join_response.status_code != 200
        and join_response.status_code != 204
    ):
        return {"status": "error", "message": "Failed to join guild"}
    return {"status": "success", "message": "User onboarded successfully"}
