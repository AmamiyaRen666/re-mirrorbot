import asyncio
import os
import shutil
import signal
import time
from datetime import datetime
from sys import executable

import psutil
import pytz
from pyrogram import idle
from telegram import ParseMode, InlineKeyboardMarkup
from telegram.ext import CommandHandler
from telegraph import Telegraph
from wserver import start_server_async

from bot import (
    OWNER_ID,
    AUTHORIZED_CHATS,
    IGNORE_PENDING_REQUESTS,
    IMAGE_URL,
    IS_VPS,
    PORT,
    alive,
    app,
    bot,
    botStartTime,
    dispatcher,
    updater,
    web,
    telegraph_token,
)
from bot.helper.ext_utils import fs_utils
from bot.helper.telegram_helper import button_build
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import *

from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from .modules import (
    authorize,
    cancel_mirror,
    clone,
    count,
    delete,
    eval,
    list,
    mediainfo,
    mirror,
    mirror_status,
    reboot,
    shell,
    speedtest,
    torrent_search,
    usage,
    watch,
)

now = datetime.now(pytz.timezone("Asia/Jakarta"))


def stats(update, context):
    currentTime = get_readable_time(time.time() - botStartTime)
    current = now.strftime("%Y/%m/%d %I:%M:%S %p")
    total, used, free = shutil.disk_usage(".")
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    stats = (
        f"<b>Bot berjalan:</b> <code>{currentTime}</code>\n"
        f"<b>Ruang Penyimpnan total:</b> <code>{total}</code>\n"
        f"<b>Digunakan:</b> <code>{used}</code> "
        f"<b>Bebas:</b> <code>{free}</code>\n\n"
        f"<b>Upload:</b> <code>{sent}</code>\n"
        f"<b>Download:</b> <code>{recv}</code>\n\n"
        f"<b>CPU:</b> <code>{cpuUsage}%</code> "
        f"<b>RAM:</b> <code>{memory}%</code> "
        f"<b>HDD:</b> <code>{disk}%</code>"
    )
    update.effective_message.reply_photo(
        IMAGE_URL, stats, parse_mode=ParseMode.HTML
    )  # noqa: E501


def start(update, context):
    buttons = button_build.ButtonMaker()
    buttons.buildbutton("Repo", "https://github.com/Ncode2014/re-cerminbot")
    buttons.buildbutton("Support Group", "https://t.me/rumahmirorr")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    if (
        CustomFilters.authorized_user(update)
        or CustomFilters.authorized_chat(update)
        or update.message.chat.type == "private"
    ):
        start_string = f"""
Bot ini dapat mencerminkan semua tautan Anda ke Google Drive!
Tipe /{BotCommands.HelpCommand} untuk mendapatkan daftar perintah yang tersedia
"""
        sendMarkup(start_string, context.bot, update, reply_markup)
    else:
        sendMarkup(
            "Ups! bukan pengguna Resmi.\nTolong deploy bot <b>re-cerminbot</b> buat kamu sendiri.",  # noqa: E501
            context.bot,
            update,
            reply_markup,
        )


def restart(update, context):
    restart_message = sendMessage(
        "Mulai ulang, Harap tunggu!", context.bot, update
    )  # noqa: E501
    # Save restart message object in order to reply to it after restarting
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    alive.terminate()
    web.terminate()
    os.execl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Mulai Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f"{end_time - start_time} ms", reply)


def log(update, context):
    sendLogFile(context.bot, update)


def bot_help(update, context):
    help_string_telegraph = f'''<br>
<b>/{BotCommands.HelpCommand}</b>: To get this message
<br><br>
<b>/{BotCommands.MirrorCommand}</b> [download_url][magnet_link]: Start mirroring the link to Google Drive.
<br><br>
<b>/{BotCommands.TarMirrorCommand}</b> [download_url][magnet_link]: Start mirroring and upload the archived (.tar) version of the download
<br><br>
<b>/{BotCommands.ZipMirrorCommand}</b> [download_url][magnet_link]: Start mirroring and upload the archived (.zip) version of the download
<br><br>
<b>/{BotCommands.UnzipMirrorCommand}</b> [download_url][magnet_link]: Starts mirroring and if downloaded file is any archive, extracts it to Google Drive
<br><br>
<b>/{BotCommands.QbMirrorCommand}</b> [magnet_link]: Start Mirroring using qBittorrent, Use /{BotCommands.QbMirrorCommand} s to select files before downloading
<br><br>
<b>/{BotCommands.QbTarMirrorCommand}</b> [magnet_link]: Start mirroring using qBittorrent and upload the archived (.tar) version of the download
<br><br>
<b>/{BotCommands.QbZipMirrorCommand}</b> [magnet_link]: Start mirroring using qBittorrent and upload the archived (.zip) version of the download
<br><br>
<b>/{BotCommands.QbUnzipMirrorCommand}</b> [magnet_link]: Starts mirroring using qBittorrent and if downloaded file is any archive, extracts it to Google Drive
<br><br>
<b>/{BotCommands.CloneCommand}</b> [drive_url]: Copy file/folder to Google Drive
<br><br>
<b>/{BotCommands.CountCommand}</b> [drive_url]: Count file/folder of Google Drive Links
<br><br>
<b>/{BotCommands.DeleteCommand}</b> [drive_url]: Delete file from Google Drive (Only Owner & Sudo)
<br><br>
<b>/{BotCommands.WatchCommand}</b> [youtube-dl supported link]: Mirror through youtube-dl. Click /{BotCommands.WatchCommand} for more help
<br><br>
<b>/{BotCommands.TarWatchCommand}</b> [youtube-dl supported link]: Mirror through youtube-dl and tar before uploading
<br><br>
<b>/{BotCommands.ZipWatchCommand}</b> [youtube-dl supported link]: Mirror through youtube-dl and zip before uploading
<br><br>
<b>/{BotCommands.CancelMirror}</b>: Reply to the message by which the download was initiated and that download will be cancelled
<br><br>
<b>/{BotCommands.CancelAllCommand}</b>: Cancel all running tasks
<br><br>
<b>/{BotCommands.ListCommand}</b> [search term]: Searches the search term in the Google Drive, If found replies with the link
<br><br>
<b>/{BotCommands.StatusCommand}</b>: Shows a status of all the downloads
<br><br>
<b>/{BotCommands.StatsCommand}</b>: Show Stats of the machine the bot is hosted on
'''

    help_string = f'''
/{BotCommands.PingCommand}: Check how long it takes to Ping the Bot

/{BotCommands.AuthorizeCommand}: Otorisasi obrolan atau pengguna untuk menggunakan BOT (hanya dapat dipanggil oleh pemilik & sudo bot)

/{BotCommands.UnAuthorizeCommand}: Tidak sah obrolan atau pengguna untuk menggunakan BOT (hanya dapat dipanggil oleh pemilik & sudo bot)

/{BotCommands.AuthorizedUsersCommand}: Tampilkan pengguna yang berwenang (hanya pemilik & sudo)

/{BotCommands.AddSudoCommand}: Tambahkan pengguna sudo (hanya pemilik)

/{BotCommands.RmSudoCommand}: Hapus pengguna sudo (hanya pemilik)

/{BotCommands.RestartCommand}: Mulai ulang bot.

/{BotCommands.LogCommand}: Dapatkan file log bot.Berguna untuk mendapatkan laporan kecelakaan

/{BotCommands.UsageCommand}: Untuk melihat statistik Heroku Dyno (hanya pemilik & sudo)

/{BotCommands.SpeedCommand}: Periksa kecepatan internet tuan rumah

/{BotCommands.MediaInfoCommand}: Dapatkan info terperinci tentang Media Jawab (hanya untuk file telegram)

/{BotCommands.TsHelpCommand}: Get help for Torrent search module
'''
    help = Telegraph(access_token=telegraph_token).create_page(title = 'Slam Mirrorbot Search', author_name='Slam Mirrorbot',
                                                               author_url='https://github.com/SlamDevs/slam-mirrorbot', html_content=help_string_telegraph)["path"]
    button = button_build.ButtonMaker()
    button.buildbutton("Other Commands", f"https://telegra.ph/{help}")
    reply_markup = InlineKeyboardMarkup(button.build_menu(1))
    sendMarkup(help_string, context.bot, update, reply_markup)


'''
botcmds = [
    (f"{BotCommands.HelpCommand}", "Dapatkan bantuan terperinci"),
    (f"{BotCommands.MirrorCommand}", "Mulai mirroring"),
    (f"{BotCommands.TarMirrorCommand}", "Mulai mirroring dan unggah sebagai .tar"),
    (f"{BotCommands.UnzipMirrorCommand}", "Ekstrak file"),
    (f"{BotCommands.ZipMirrorCommand}", "Mulai mirroring dan unggah sebagai .zip"),
    (f"{BotCommands.CloneCommand}", "Salin file/folder ke Drive"),
    (f"{BotCommands.CountCommand}", "Hitung file/folder dari link Drive"),
    (f"{BotCommands.DeleteCommand}", "Hapus file dari drive"),
    (f'{BotCommands.QbMirrorCommand}','Mulai Mencerminkan menggunakan qBittorrent'),
    (f'{BotCommands.QbTarMirrorCommand}','Mulai mirroring dan unggah sebagai .tar menggunakan qb'),
    (f'{BotCommands.QbZipMirrorCommand}','Mulai mirroring dan unggah sebagai .zip menggunakan qb'),
    (f'{BotCommands.QbUnzipMirrorCommand}','Ekstrak file melalui qBitorrent'),
    (f"{BotCommands.WatchCommand}", "Mirror video/audio menggunakan YouTube-DL"),
    (
        f"{BotCommands.TarWatchCommand}",
        "Cermin tautan daftar putar YouTube sebagai .tar",
    ),
    (f'{BotCommands.ZipWatchCommand}','Cerminkan tautan daftar putar Youtube sebagai .zip'),
    (f"{BotCommands.CancelMirror}", "Batalkan tugas"),
    (f"{BotCommands.CancelAllCommand}", "Batalkan semua tugas"),
    (f"{BotCommands.ListCommand}", "Mencari file dalam drive"),
    (f"{BotCommands.StatusCommand}", "Dapatkan pesan status cermin"),
    (f"{BotCommands.StatsCommand}", "Statistik Penggunaan Bot."),
    (f"{BotCommands.PingCommand}", "berlomba cepat koneksi."),
    (f"{BotCommands.RestartCommand}", "Mulai ulang bot. [hanya owner/sudo]"),
    (f"{BotCommands.LogCommand}", "Dapatkan Log Bot [hanya owner/sudo]"),
    (
        f"{BotCommands.MediaInfoCommand}",
        "Dapatkan info detail tentang media yang dibalas",
    ),
    (f"{BotCommands.TsHelpCommand}", "Dapatkan bantuan untuk modul pencarian Torrent"),
]
'''


def main():
    fs_utils.start_cleanup()
    if IS_VPS:
        asyncio.get_event_loop().run_until_complete(start_server_async(PORT))
    # Check if the bot is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Berhasil memulai kembali!", chat_id, msg_id)
        os.remove(".restartmsg")
    elif OWNER_ID:
        try:
            text = "<b>Bot Restarted!</b>"
            bot.sendMessage(chat_id=OWNER_ID, text=text, parse_mode=ParseMode.HTML)
            if AUTHORIZED_CHATS:
                for i in AUTHORIZED_CHATS:
                    bot.sendMessage(chat_id=i, text=text, parse_mode=ParseMode.HTML)
        except Exception as e:
            LOGGER.warning(e)
    # bot.set_my_commands(botcmds)
    start_handler = CommandHandler(BotCommands.StartCommand, start, run_async=True)
    ping_handler = CommandHandler(
        BotCommands.PingCommand,
        ping,
        filters=CustomFilters.authorized_chat | CustomFilters.authorized_user,
        run_async=True,
    )
    restart_handler = CommandHandler(
        BotCommands.RestartCommand,
        restart,
        filters=CustomFilters.owner_filter | CustomFilters.sudo_user,
        run_async=True,
    )
    help_handler = CommandHandler(
        BotCommands.HelpCommand,
        bot_help,
        filters=CustomFilters.authorized_chat | CustomFilters.authorized_user,
        run_async=True,
    )
    stats_handler = CommandHandler(
        BotCommands.StatsCommand,
        stats,
        filters=CustomFilters.authorized_chat | CustomFilters.authorized_user,
        run_async=True,
    )
    log_handler = CommandHandler(
        BotCommands.LogCommand,
        log,
        filters=CustomFilters.owner_filter | CustomFilters.sudo_user,
        run_async=True,
    )
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("Bot Started!")
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)


app.start()
main()
idle()
