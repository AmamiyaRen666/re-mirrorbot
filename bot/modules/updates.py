# Implement By https://github.com/jusidama18
# Based on this
# https://github.com/DevsExpo/FridayUserbot/blob/master/plugins/updater.py

import subprocess
import sys
from datetime import datetime
from os import environ, execle, path, remove

import heroku3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from pyrogram import filters

from bot import app, OWNER_ID, UPSTREAM_REPO, UPSTREAM_BRANCH, bot
from bot.helper import HEROKU_URL
from bot.helper.telegram_helper.bot_commands import BotCommands

REPO_ = UPSTREAM_REPO
BRANCH_ = UPSTREAM_BRANCH


def gen_chlog(repo, diff):
    # sourcery skip: inline-immediately-returned-variable, use-join
    ch_log = ''
    d_form = "%d/%m/%y"
    for c in repo.iter_commits(diff):
        ch_log += f'• [{c.committed_datetime.strftime(d_form)}]: {c.summary} **{c.author}**\n'
    return ch_log

# Update Command


@app.on_message(
    filters.command(BotCommands.UpdateCommand) & filters.user(OWNER_ID)
)
async def update_it(client, message):
    msg_ = await message.reply_text("`Memperbarui Harap Tunggu!`")
    text = message.text.split(None, 1)[1]
    try:
        repo = Repo()
    except GitCommandError:
        return await msg_.edit(
            "**Perintah Git Tidak Valid. Silakan Laporkan Bug Ini Ke [Support Group](https://t.me/SlamMirrorSupport)**"
        )
    except InvalidGitRepositoryError:
        repo = Repo.init()
        if "upstream" in repo.remotes:
            origin = repo.remote("upstream")
        else:
            origin = repo.create_remote("upstream", REPO_)
        origin.fetch()
        repo.create_head(UPSTREAM_BRANCH, origin.refs.master)
        repo.heads.master.set_tracking_branch(origin.refs.master)
        repo.heads.master.checkout(True)
    if repo.active_branch.name != UPSTREAM_BRANCH:
        return await msg_.edit(
            f"`Sepertinya Anda Menggunakan Branch custom - {repo.active_branch.name}! Tolong beralih ke {UPSTREAM_BRANCH} Untuk membuat updater berfungsi!`"
        )
    try:
        repo.create_remote("upstream", REPO_)
    except BaseException:
        pass
    ups_rem = repo.remote("upstream")
    ups_rem.fetch(UPSTREAM_BRANCH)
    clogs = gen_chlog(repo, f'HEAD..upstream/{UPSTREAM_BRANCH}')

    if not clogs:
        await msg_.edit(f"Bot up-to-date dengan **{UPSTREAM_BRANCH}**", parse_mode="Markdown")
        return

    if text == "now":
        await msg_.edit(f"`Bot memperbarui dengan` **{UPSTREAM_BRANCH}** `Branch harap tunggu...`", parse_mode="Markdown")
        if not HEROKU_URL:
            try:
                ups_rem.pull(UPSTREAM_BRANCH)
            except GitCommandError:
                repo.git.reset("--hard", "FETCH_HEAD")
            await subprocess.run(["pip3", "install", "--no-cache-dir", "-r", "requirements.txt"])
            await msg_.edit("`Diperbarui! Beri saya waktu untuk memulai kembali!`")
            with open("./aria.sh", 'rb') as file:
                script = file.read()
            subprocess.call("./aria.sh", shell=True)
            args = [sys.executable, "-m", "bot"]
            execle(sys.executable, *args, environ)
        else:
            await msg_.edit("`Heroku terdeteksi! Pushing, Mohon tunggu!`")
            ups_rem.fetch(UPSTREAM_BRANCH)
            repo.git.reset("--hard", "FETCH_HEAD")
            if "heroku" in repo.remotes:
                remote = repo.remote("heroku")
                remote.set_url(HEROKU_URL)
            else:
                remote = repo.create_remote("heroku", HEROKU_URL)
            try:
                remote.push(refspec="HEAD:refs/heads/master", force=True)
            except BaseException as error:
                await msg_.edit(f"**Updater Error** \nTraceBack : `{error}`")
                return repo.__del__()
            await msg_.edit(f"`Updated berhasil! \n\nPeriksa konfigurasi Anda dengan` `/{BotCommands.ConfigMenuCommand}`")
    else:
        await msg_.edit(f"**Pembaruan baru tersedia**\n\nDari [REPO]({REPO_})\nCHANGELOG:\n\n{clogs}\n\nlakukan `/perbarui now` Untuk memperbarui bot..", parse_mode="Markdown", disable_web_page_preview=True)
        return
