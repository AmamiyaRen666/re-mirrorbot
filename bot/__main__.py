import shutil, psutil
import signal
import os

from pyrogram import idle
from bot import app
from sys import executable
from datetime import datetime
import pytz
import time

from telegram import ParseMode, BotCommand
from telegram.ext import CommandHandler
from bot import bot, dispatcher, updater, botStartTime, IMAGE_URL, IGNORE_PENDING_REQUESTS
from bot.helper.ext_utils import fs_utils
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import *
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper import button_build
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, shell, eval, search, delete, speedtest, usage, mediainfo, count, config, updates

now=datetime.now(pytz.timezone('Asia/Jakarta'))


def stats(update, context):
    currentTime = get_readable_time(time.time() - botStartTime)
    current = now.strftime('%Y/%m/%d %I:%M:%S %p')
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    stats = f'<b>Waktu Aktif Bot:</b> {currentTime}\n' \
            f'<b>Waktu mulai:</b> {current}\n' \
            f'<b>Total Ruang Disk:</b> {total}\n' \
            f'<b>Digunakan:</b> {used}  ' \
            f'<b>Bebas:</b> {free}\n\n' \
            f'📊Penggunaan Data📊\n<b>Upload:</b> {sent}\n' \
            f'<b>Download:</b> {recv}\n\n' \
            f'<b>CPU:</b> {cpuUsage}%\n' \
            f'<b>RAM:</b> {memory}%\n' \
            f'<b>HDD:</b> {disk}%'
    update.effective_message.reply_photo(IMAGE_URL, stats, parse_mode=ParseMode.HTML)


def start(update, context):
    start_string = f'''
This bot can mirror all your links to Google Drive!
Type /{BotCommands.HelpCommand} to get a list of available commands
'''
    buttons = button_build.ButtonMaker()
    buttons.buildbutton("Repo", "https://github.com/breakdowns/slam-mirrorbot")
    buttons.buildbutton("Support Group", "https://t.me/SlamMirrorSupport")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    LOGGER.info('UID: {} - UN: {} - MSG: {}'.format(update.message.chat.id, update.message.chat.username, update.message.text))
    uptime = get_readable_time((time.time() - botStartTime))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        if update.message.chat.type == "private" :
            sendMessage(f"Hey I'm Alive 🙂\nSince: <code>{uptime}</code>", context.bot, update)
        else :
            update.effective_message.reply_photo(IMAGE_URL, start_string, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    else :
        sendMessage(f"Oops! not a Authorized user.", context.bot, update)


def restart(update, context):
    restart_message = sendMessage("Restarting, Please wait!", context.bot, update)
    # Save restart message object in order to reply to it after restarting
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    os.execl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update)


def bot_help(update, context):
    help_string_adm = f'''
/{BotCommands.HelpCommand}: Untuk mendapatkan pesan ini

/{BotCommands.MirrorCommand} [download_url][magnet_link]: Mulai mirroring tautan ke Google Drive.

/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: Mulai mirroring dan jika file yang diunduh adalah arsip apa pun, ekstrak ke Google Drive

/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Mulai mirroring dan unggah versi unduhan (.tar) yang diarsipkan

/{BotCommands.CloneCommand}: Salin file/folder ke Google Drive

/{BotCommands.CountCommand}: Hitung file/folder dari Link Google Drive

/{BotCommands.DeleteCommand} [link]: Hapus file dari Google Drive (Hanya Pemilik & Sudo)

/{BotCommands.WatchCommand} [youtube-dl supported link]: Mirror through youtube-dl. Click /{BotCommands.WatchCommand} for more help.

/{BotCommands.TarWatchCommand} [youtube-dl supported link]: Mirror through youtube-dl and tar before uploading

/{BotCommands.CancelMirror}: Balas pesan di mana unduhan dimulai dan unduhan itu akan dibatalkan

/{BotCommands.StatusCommand}: Menunjukkan status semua unduhan

/{BotCommands.ListCommand} [search term]: Mencari istilah pencarian di Google Drive, jika ditemukan balasan dengan balas tautan

/{BotCommands.StatsCommand}: Tampilkan Statistik mesin tempat bot dihosting

/{BotCommands.AuthorizeCommand}: Otorisasi obrolan atau pengguna untuk menggunakan bot (Hanya dapat dipanggil oleh Pemilik & Sudo bot)

/{BotCommands.UnAuthorizeCommand}: Batalkan otorisasi obrolan atau pengguna untuk menggunakan bot (Hanya dapat dipanggil oleh Pemilik & Sudo bot)

/{BotCommands.AuthorizedUsersCommand}: Tampilkan pengguna resmi (Hanya Pemilik & Sudo)

/{BotCommands.AddSudoCommand}: Tambahkan pengguna Sudo (Hanya Pemilik)

/{BotCommands.RmSudoCommand}: Hapus pengguna Sudo (Hanya Pemilik)

/{BotCommands.LogCommand}: Dapatkan file log bot. Berguna untuk mendapatkan laporan kerusakan

/{BotCommands.ConfigMenuCommand}: Get Info Menu about bot config (Owner Only).

/{BotCommands.UpdateCommand}: Perbarui Bot dari Repo Github. (Hanya Pemilik).

/{BotCommands.UsageCommand}: To see Heroku Dyno Stats (Owner & Sudo only).

/{BotCommands.SpeedCommand}: Periksa Kecepatan Internet Tuan Rumah

/{BotCommands.MediaInfoCommand}: Dapatkan info detail tentang media yang dibalas (Hanya untuk file Telegram).

/{BotCommands.ShellCommand}: Jalankan perintah di Shell (Terminal).

/tshelp: Get help for Torrent search module.
'''

    help_string = f'''
/{BotCommands.HelpCommand}: Untuk mendapatkan pesan ini

/{BotCommands.MirrorCommand} [download_url][magnet_link]: Mulai mirroring tautan ke Google Drive.

/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: Mulai mirroring dan jika file yang diunduh adalah arsip apa pun, ekstrak ke Google Drive

/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Mulai mirroring dan unggah versi unduhan (.tar) yang diarsipkan

/{BotCommands.CloneCommand}: Salin file/folder ke Google Drive

/{BotCommands.CountCommand}: Hitung file/folder dari Link Google Drive

/{BotCommands.WatchCommand} [youtube-dl supported link]: Mirror through youtube-dl. Click /{BotCommands.WatchCommand} for more help.

/{BotCommands.TarWatchCommand} [youtube-dl supported link]: Mirror through youtube-dl and tar before uploading

/{BotCommands.CancelMirror}: Balas pesan di mana unduhan dimulai dan unduhan itu akan dibatalkan

/{BotCommands.StatusCommand}: Menunjukkan status semua unduhan

/{BotCommands.ListCommand} [search term]: Mencari istilah pencarian di Google Drive, jika ditemukan balasan dengan balas tautan

/{BotCommands.StatsCommand}: Tampilkan Statistik mesin tempat bot dihosting

/{BotCommands.SpeedCommand}: Periksa Kecepatan Internet Tuan Rumah

/{BotCommands.MediaInfoCommand}: Dapatkan info detail tentang media yang dibalas (Hanya untuk file Telegram).

/tshelp: Get help for Torrent search module.
'''

    if CustomFilters.sudo_user(update) or CustomFilters.owner_filter(update):
        sendMessage(help_string_adm, context.bot, update)
    else:
        sendMessage(help_string, context.bot, update)


botcmds = [
BotCommand(f'{BotCommands.MirrorCommand}', 'Mulai Mencerminkan'),
BotCommand(f'{BotCommands.TarMirrorCommand}','Unggah file tar (zip)'),
BotCommand(f'{BotCommands.UnzipMirrorCommand}','Ekstrak file'),
BotCommand(f'{BotCommands.CloneCommand}','Salin file/folder ke Drive'),
BotCommand(f'{BotCommands.CountCommand}','Hitung file/folder dari Link Drive'),
BotCommand(f'{BotCommands.WatchCommand}','Mirror YT-DL support link'),
BotCommand(f'{BotCommands.TarWatchCommand}','Mirror Youtube playlist link as tar'),
BotCommand(f'{BotCommands.CancelMirror}','batalkan tugas'),
BotCommand(f'{BotCommands.CancelAllCommand}','batalkan semua tugas'),
BotCommand(f'{BotCommands.DeleteCommand}','Hapus file dari Drive'),
BotCommand(f'{BotCommands.ListCommand}',' [query] Mencari file di Drive'),
BotCommand(f'{BotCommands.StatusCommand}','Dapatkan pesan Status Cermin'),
BotCommand(f'{BotCommands.StatsCommand}','Statistik Penggunaan Bot'),
BotCommand(f'{BotCommands.HelpCommand}','Dapatkan Bantuan Mendetail'),
BotCommand(f'{BotCommands.MediaInfoCommand}','Dapatkan info detail tentang media yang dibalas'),
BotCommand(f'{BotCommands.SpeedCommand}','Periksa Kecepatan Server'),
BotCommand(f'{BotCommands.LogCommand}','Catatan Bot [hanya owner/sudo]'),
BotCommand(f'{BotCommands.RestartCommand}','Mulai ulang bot [hanya owner/sudo]')]


def main():
    fs_utils.start_cleanup()
    # Check if the bot is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Berhasil memulai kembali!", chat_id, msg_id)
        os.remove(".restartmsg")
    bot.set_my_commands(botcmds)

    start_handler = CommandHandler(BotCommands.StartCommand, start, run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
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
