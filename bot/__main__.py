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
from telegram import ParseMode
from telegram.ext import CommandHandler
from wserver import start_server_async

from bot import (IGNORE_PENDING_REQUESTS, IMAGE_URL, IS_VPS, SERVER_PORT, app,
                 bot, botStartTime, dispatcher, alive, updater)
from bot.helper.ext_utils import fs_utils
from bot.helper.telegram_helper import button_build
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import *

from .helper.ext_utils.bot_utils import (get_readable_file_size,
                                         get_readable_time)
from .helper.telegram_helper.filters import CustomFilters
from .modules import (authorize, cancel_mirror, clone, count, delete,
                      eval, list, mediainfo, mirror, mirror_status, shell,
                      speedtest, torrent_search, reboot, usage, watch)

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
    disk = psutil.disk_usage('/').percent
    stats = f'<b>Bot berjalan:</b> <code>{currentTime}</code>\n' \
            f'<b>Ruang Penyimpnan total:</b> <code>{total}</code>\n' \
            f'<b>Digunakan:</b> <code>{used}</code> ' \
            f'<b>Bebas:</b> <code>{free}</code>\n\n' \
            f'<b>Upload:</b> <code>{sent}</code>\n' \
            f'<b>Download:</b> <code>{recv}</code>\n\n' \
            f'<b>CPU:</b> <code>{cpuUsage}%</code> ' \
            f'<b>RAM:</b> <code>{memory}%</code> ' \
            f'<b>HDD:</b> <code>{disk}%</code>'
    update.effective_message.reply_photo(
        IMAGE_URL, stats, parse_mode=ParseMode.HTML)


def start(update, context):  # sourcery skip: move-assign
    start_string = f"""
Bot ini dapat mencerminkan semua tautan Anda ke Google Drive!
Tipe /{BotCommands.HelpCommand} untuk mendapatkan daftar perintah yang tersedia
"""
    buttons = button_build.ButtonMaker()
    buttons.buildbutton("Repo", "https://github.com/Ncode2014/re-cerminbot")
    buttons.buildbutton("Support Group", "https://t.me/rumahmirorr")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update) or update.message.chat.type == "private":
        sendMarkup(start_string, context.bot, update, reply_markup)
    else:
        sendMarkup(f"Ups! bukan pengguna Resmi.\nTolong deploy bot <b>re-cerminbot</b> buat kamu sendiri.",
                   context.bot, update, reply_markup)


def restart(update, context):
    restart_message = sendMessage(
        "Mulai ulang, Harap tunggu!", context.bot, update)
    # Save restart message object in order to reply to it after restarting
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    alive.terminate()
    os.execl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Mulai Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f"{end_time - start_time} ms", reply)


def log(update, context):
    sendLogFile(context.bot, update)


def bot_help(update, context):
    help_string_adm = f"""
/{BotCommands.HelpCommand}: Untuk mendapatkan pesan ini

/{BotCommands.MirrorCommand} [download_url][magnet_link]: Mulai mirroring tautan ke Google Drive. Gunakan /{BotCommands.MirrorCommand} qb untuk mirror menggunakan qBittorrent, dan gunakan /{BotCommands.MirrorCommand} qbs untuk memilih file sebelum download

/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Mulai mirroring dan unggah yang diarsipkan (.tar) versi unduhan

/{BotCommands.ZipMirrorCommand} [download_url][magnet_link]: Mulai mirroring dan unggah versi unduhan yang diarsipkan (.zip)

/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: Mulai mirroring dan file yang diunduh adalah arsip, mengekstraknya ke Google Drive

/{BotCommands.CloneCommand} [drive_url]: Salin file/folder ke Google Drive

/{BotCommands.CountCommand} [drive_url]: Hitung file/folder dari Google Drive Links

/{BotCommands.DeleteCommand} [drive_url]: Hapus file dari Google Drive (Hanya Pemilik & Sudo)

/{BotCommands.WatchCommand} [youtube-dlp supported link]: Cermin melalui youtube-dlp. Ketik /{BotCommands.WatchCommand} atau ketik /bantuan

/{BotCommands.TarWatchCommand} [youtube-dlp supported link]: Cermin melalui youtube-dlp dan tar sebelum mengunggah

/{BotCommands.CancelMirror}: Balas pesan di mana unduhan dimulai dan unduhan itu akan dibatalkan

/{BotCommands.CancelAllCommand}: Batalkan semua tugas yang sedang berjalan

/{BotCommands.ListCommand} [search term]: Mencari istilah pencarian di Google Drive, Jika ditemukan balasan dengan tautan

/{BotCommands.StatusCommand}: Menunjukkan status semua unduhan

/{BotCommands.StatsCommand}: Tampilkan Statistik Mesin The Bot diselenggarakan

/{BotCommands.PingCommand}: Periksa berapa lama untuk melakukan ping bot

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

/{BotCommands.ShellCommand}: Jalankan perintah di Shell (Terminal)

/{BotCommands.ExecHelpCommand}: Dapatkan bantuan untuk modul pelaksana

/{BotCommands.TsHelpCommand}: Dapatkan bantuan untuk modul pencarian torrent
"""

    help_string = f"""
/{BotCommands.HelpCommand}: Untuk mendapatkan pesan ini

/{BotCommands.MirrorCommand} [download_url][magnet_link]: Mulai mirroring tautan ke Google Drive. Gunakan /{BotCommands.MirrorCommand} qb untuk mirror menggunakan qBittorrent, dan gunakan /{BotCommands.MirrorCommand} qbs untuk memilih file sebelum download

/{BotCommands.ZipMirrorCommand} [download_url][magnet_link]: Mulai mirroring dan unggah versi unduhan yang diarsipkan (.zip)

/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Mulai mirroring dan unggah diarsipkan (.tar) version of the download

/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: Mulai mirroring dan file yang diunduh adalah arsip, mengekstraknya ke Google Drive

/{BotCommands.CloneCommand} [drive_url]: Salin file / folder ke Google Drive

/{BotCommands.CountCommand} [drive_url]: Hitung file / folder dari tautan Google Drive

/{BotCommands.WatchCommand} [youtube-dlp supported link]: Mirror through youtube-dl. Click /{BotCommands.WatchCommand} for more help

/{BotCommands.TarWatchCommand} [youtube-dlp supported link]: Mirror through youtube-dl and tar before uploading

/{BotCommands.CancelMirror}: Membalas pesan dimana undangan diinisiasi dan unduhan akan dibatalkan

/{BotCommands.ListCommand} [search term]: Mencari istilah pencarian di Google Drive, jika ditemukan balasan dengan tautan

/{BotCommands.StatusCommand}: Menunjukkan status semua unduhan

/{BotCommands.StatsCommand}: Tampilkan Statistik Mesin The Bot diselenggarakan

/{BotCommands.PingCommand}: Periksa berapa lama untuk melakukan ping bot

/{BotCommands.SpeedCommand}: Periksa kecepatan internet tuan rumah

/{BotCommands.MediaInfoCommand}: Dapatkan info terperinci tentang Media Jawab (hanya untuk file telegram)

/{BotCommands.TsHelpCommand}: Dapatkan bantuan untuk modul pencarian torrent
"""

    if CustomFilters.sudo_user(update) or CustomFilters.owner_filter(update):
        sendMessage(help_string_adm, context.bot, update)
    else:
        sendMessage(help_string, context.bot, update)


botcmds = [
    (f'{BotCommands.HelpCommand}', 'Dapatkan bantuan terperinci'),
    (f'{BotCommands.MirrorCommand}', 'Mulai mirroring'),
    (f'{BotCommands.TarMirrorCommand}',
     'Mulai mirroring dan unggah sebagai .tar'),
    (f'{BotCommands.UnzipMirrorCommand}', 'Ekstrak file'),
    (f'{BotCommands.ZipMirrorCommand}',
     'Mulai mirroring dan unggah sebagai .zip'),
    (f'{BotCommands.CloneCommand}', 'Salin file/folder ke Drive'),
    (f'{BotCommands.CountCommand}', 'Hitung file/folder dari link Drive'),
    (f'{BotCommands.DeleteCommand}', 'Hapus file dari drive'),
    (f'{BotCommands.WatchCommand}', 'Mirror video/audio menggunakan YouTube-DL'),
    (f'{BotCommands.TarWatchCommand}',
     'Cermin tautan daftar putar YouTube sebagai .tar'),
    (f'{BotCommands.CancelMirror}', 'Batalkan tugas'),
    (f'{BotCommands.CancelAllCommand}', 'Batalkan semua tugas'),
    (f'{BotCommands.ListCommand}', 'Mencari file dalam drive'),
    (f'{BotCommands.StatusCommand}', 'Dapatkan pesan status cermin'),
    (f'{BotCommands.StatsCommand}', 'Statistik Penggunaan Bot.'),
    (f'{BotCommands.PingCommand}', 'berlomba cepat koneksi.'),
    (f'{BotCommands.RestartCommand}', 'Mulai ulang bot. [hanya owner/sudo]'),
    (f'{BotCommands.LogCommand}', 'Dapatkan Log Bot [hanya owner/sudo]'),
    (f'{BotCommands.MediaInfoCommand}',
     'Dapatkan info detail tentang media yang dibalas'),
    (f'{BotCommands.TsHelpCommand}',
     'Dapatkan bantuan untuk modul pencarian torrent')
]


def main():
    fs_utils.start_cleanup()

    if IS_VPS:
        asyncio.get_event_loop().run_until_complete(start_server_async(SERVER_PORT))

    # Check if the bot is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Berhasil memulai kembali!", chat_id, msg_id)
        os.remove(".restartmsg")
    bot.set_my_commands(botcmds)

    start_handler = CommandHandler(
        BotCommands.StartCommand, start, run_async=True)
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
