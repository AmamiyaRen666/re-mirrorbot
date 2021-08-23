import asyncio
import os
import shlex
import heroku3

from functools import wraps
from html_telegraph_poster import TelegraphPoster
from bot import HEROKU_API_KEY, HEROKU_APP_NAME

# Preparing For Setting Config
# Implement by https://github.com/jusidama18 and Based on this
# https://github.com/DevsExpo/FridayUserbot/blob/master/plugins/heroku_helpers.py

heroku_client = None
if HEROKU_API_KEY:
    heroku_client = heroku3.from_key(HEROKU_API_KEY)


def check_heroku(func):
    @wraps(func)
    async def heroku_cli(client, message):
        heroku_app = None
        if not heroku_client:
            await message.reply_text(
                "`Please Add HEROKU_API_KEY Key For This To Function To Work!`",
                parse_mode="markdown"
            )
        elif not HEROKU_APP_NAME:
            await message.reply_text(
                "`Please Add HEROKU_APP_NAME For This To Function To Work!`",
                parse_mode="markdown"
            )
        if HEROKU_APP_NAME and heroku_client:
            try:
                heroku_app = heroku_client.app(HEROKU_APP_NAME)
            except BaseException:
                await message.reply_text(
                    message,
                    "`Heroku Api Key And App Name Doesn't Match!`",
                    parse_mode="markdown"
                )
            if heroku_app:
                await func(client, message, heroku_app)

    return heroku_cli


def post_to_telegraph(a_title: str, content: str) -> str:
    """ Create a Telegram Post using HTML Content """
    post_client = TelegraphPoster(use_api=True)
    auth_name = "slam-mirrorbot"
    post_client.create_api_token(auth_name)
    post_page = post_client.post(
        title=a_title,
        author=auth_name,
        author_url="https://github.com/breakdowns/slam-mirrorbot",
        text=content,
    )
    return post_page["url"]


async def runcmd(cmd: str) -> tuple[str, str, int, int]:
    """ run command in terminal """
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )


# Solves ValueError: No closing quotation by removing ' or " in file name
def safe_filename(path_):
    if path_ is None:
        return
    safename = path_.replace("'", "").replace('"', "")
    if safename != path_:
        os.rename(path_, safename)
    return safename
