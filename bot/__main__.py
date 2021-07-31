import shutil
import psutil
import signal
import os

from pyrogram import idle
from bot import app
from sys import executable
from datetime import datetime
import pytz
import time

from telegram import ParseMode
from telegram.ext import CommandHandler
from bot import bot, dispatcher, updater, botStartTime, IMAGE_URL, IGNORE_PENDING_REQUESTS
from bot.helper.ext_utils import fs_utils
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import *
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper import button_build
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, shell, eval, torrent_search, delete, speedtest, usage, mediainfo, count, config, updates

now = datetime.now(pytz.timezone('Asia/Jakarta'))


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
    update.effective_message.reply_photo(IMAGE_URL,
                                         stats,
                                         parse_mode=ParseMode.HTML)


def start(update, context):
    start_string = f'''
Bot ini dapat mencerminkan semua tautan Anda ke Google Drive!
Tipe /{BotCommands.HelpCommand} untuk mendapatkan daftar perintah yang tersedia
'''
    buttons = button_build.ButtonMaker()
    buttons.buildbutton("Repo", "https://github.com/breakdowns/slam-aria-mirror-bot")
    buttons.buildbutton("Support Group", "https://t.me/SlamMirrorSupport")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    LOGGER.info('UID: {} - UN: {} - MSG: {}'.format(
        update.message.chat.id, update.message.chat.username,
        update.message.text))
    uptime = get_readable_time(time.time() - botStartTime)
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(
            update):
        if update.message.chat.type == "private":
            sendMessage(f"Hei aku hidup 🙂\nSejak: <code>{uptime}</code>",
                        context.bot, update)
        else:
            update.effective_message.reply_photo(IMAGE_URL,
                                                 start_string,
                                                 parse_mode=ParseMode.MARKDOWN,
                                                 reply_markup=reply_markup)
    else:
        sendMessage(f"Ups! bukan pengguna Resmi.", context.bot, update)


def restart(update, context):
    restart_message = sendMessage("Mulai ulang, Harap tunggu!", context.bot,
                                  update)
    # Save restart message object in order to reply to it after restarting
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    os.execl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Mulai Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update)


def bot_help(update, context):
    help_string_adm = f'''
/{BotCommands.HelpCommand}: Untuk mendapatkan pesan ini

/{BotCommands.MirrorCommand} [download_url][magnet_link]: Mulai mirroring tautan ke Google Drive

/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Mulai mirroring dan unggah yang diarsipkan (.tar) versi unduhan

/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: Mulai mirroring dan jika file yang diunduh adalah arsip apa pun, ekstrak ke Google Drive

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

/{BotCommands.ConfigMenuCommand}: Dapatkan Info Menu Tentang Bot Config (Hanya Pemilik)

/{BotCommands.UpdateCommand}: Pembaruan bot dari repo upstream (hanya pemilik)

/{BotCommands.UsageCommand}: Untuk melihat statistik Heroku Dyno (hanya pemilik & sudo)

/{BotCommands.SpeedCommand}: Periksa kecepatan internet tuan rumah

/{BotCommands.MediaInfoCommand}: Dapatkan info terperinci tentang Media Jawab (hanya untuk file telegram)

/{BotCommands.ShellCommand}: Jalankan perintah di Shell (Terminal)

/{BotCommands.ExecHelpCommand}: Dapatkan bantuan untuk modul pelaksana

/{BotCommands.TsHelpCommand}: Dapatkan bantuan untuk modul pencarian torrent
'''

    help_string = f'''
/{BotCommands.HelpCommand}: Untuk mendapatkan pesan ini

/{BotCommands.MirrorCommand} [download_url][magnet_link]: Mulai Mencerminkan tautan ke Google Drive

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
'''

    if CustomFilters.sudo_user(update) or CustomFilters.owner_filter(update):
        sendMessage(help_string_adm, context.bot, update)
    else:
        sendMessage(help_string, context.bot, update)


botcmds = [
    (f'{BotCommands.HelpCommand}', 'Dapatkan Bantuan Mendetail'),
    (f'{BotCommands.MirrorCommand}', 'Mulai Mencerminkan'),
    (f'{BotCommands.TarMirrorCommand}',
     'Mulai mirroring dan unggah sebagai .tar'),
    (f'{BotCommands.UnzipMirrorCommand}', 'Ekstrak file'),
    (f'{BotCommands.CloneCommand}', 'Salin file/folder ke Drive'),
    (f'{BotCommands.CountCommand}', 'Hitung file/folder tautan Drive'),
    (f'{BotCommands.DeleteCommand}', 'Hapus file dari Drive'),
    (f'{BotCommands.WatchCommand}', 'Tautan dukungan Mirror Youtube-dlp'),
    (f'{BotCommands.TarWatchCommand}',
     'Cerminkan tautan daftar putar Youtube sebagai .tar'),
    (f'{BotCommands.CancelMirror}', 'Membatalkan tugas'),
    (f'{BotCommands.CancelAllCommand}', 'Batalkan semua tugas'),
    (f'{BotCommands.ListCommand}', 'Mencari file di Drive'),
    (f'{BotCommands.StatusCommand}', 'Dapatkan pesan Status Cermin'),
    (f'{BotCommands.StatsCommand}', 'Statistik Penggunaan Bot'),
    (f'{BotCommands.PingCommand}', 'Ping Bot'),
    (f'{BotCommands.RestartCommand}', 'Mulai ulang bot [owner/sudo only]'),
    (f'{BotCommands.LogCommand}', 'Dapatkan Log Bot [owner/sudo only]'),
    (f'{BotCommands.MediaInfoCommand}',
     'Dapatkan info detail tentang media yang dibalas'),
    (f'{BotCommands.TsHelpCommand}',
     'Dapatkan bantuan untuk modul pencarian Torrent')
]


def main():
    fs_utils.start_cleanup()
    # Check if the bot is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Berhasil memulai kembali!", chat_id, msg_id)
        os.remove(".restartmsg")
    bot.set_my_commands(botcmds)

    start_handler = CommandHandler(BotCommands.StartCommand,
                                   start,
                                   run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand,
                                  ping,
                                  filters=CustomFilters.authorized_chat |
                                  CustomFilters.authorized_user,
                                  run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand,
                                     restart,
                                     filters=CustomFilters.owner_filter |
                                     CustomFilters.sudo_user,
                                     run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help,
                                  filters=CustomFilters.authorized_chat |
                                  CustomFilters.authorized_user,
                                  run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats,
                                   filters=CustomFilters.authorized_chat |
                                   CustomFilters.authorized_user,
                                   run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand,
                                 log,
                                 filters=CustomFilters.owner_filter |
                                 CustomFilters.sudo_user,
                                 run_async=True)
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
