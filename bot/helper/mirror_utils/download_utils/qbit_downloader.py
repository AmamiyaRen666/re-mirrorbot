# Implement By - @anasty17 (https://github.com/breakdowns/slam-mirrorbot/commit/0bfba523f095ab1dccad431d72561e0e002e7a59)
# (c) https://github.com/breakdowns/slam-mirrorbot
# (c) https://github.com/yash-dk/TorToolkit-Telegram for original implemented on TorToolkit-Telegram repo
# All rights reserved

import logging
import os
import random
import shutil
import string
import time
from fnmatch import fnmatch
from urllib.parse import parse_qs, urlparse

import qbittorrentapi as qba
from telegram import InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from torrentool.api import Torrent

from bot import (BASE_URL, TAR_UNZIP_LIMIT, TORRENT_DIRECT_LIMIT, dispatcher,
                 download_dict, download_dict_lock, get_client)
from bot.helper.ext_utils.bot_utils import (MirrorStatus, check_limit,
                                            get_readable_file_size,
                                            getDownloadByGid, new_thread,
                                            setInterval)
from bot.helper.mirror_utils.status_utils.qbit_download_status import \
    QbDownloadStatus
from bot.helper.telegram_helper import button_build
from bot.helper.telegram_helper.message_utils import *

LOGGER = logging.getLogger(__name__)


class qbittorrent:
    def __init__(self):
        self.update_interval = 2
        self.meta_time = time.time()
        self.stalled_time = time.time()
        self.checked = False

    @new_thread
    def add_torrent(self, link, dire, listener, qbitsel):  # sourcery no-metrics
        self.client = get_client()
        self.listener = listener
        self.dire = dire
        self.qbitsel = qbitsel
        is_file = False
        count = 0
        pincode = ""
        try:
            if os.path.exists(link):
                is_file = True
                self.ext_hash = get_hash_file(link)
            else:
                self.ext_hash = get_hash_magnet(link)
            tor_info = self.client.torrents_info(torrent_hashes=self.ext_hash)
            if len(tor_info) > 0:
                sendMessage(
                    "Torrent ini sudah ada dalam daftar.", listener.bot, listener.update
                )
                return
            if is_file:
                op = self.client.torrents_add(torrent_files=[link], save_path=dire)
                os.remove(link)
            else:
                op = self.client.torrents_add(link, save_path=dire)
            if op.lower() == "ok.":
                tor_info = self.client.torrents_info(torrent_hashes=self.ext_hash)
                if len(tor_info) == 0:
                    while True:
                        if time.time() - self.meta_time >= 300:
                            sendMessage(
                                "Torrent tidak ditambahkan. Laporkan ketika Anda melihat kesalahan ini",
                                listener.bot,
                                listener.update,
                            )
                            return False
                        tor_info = self.client.torrents_info(
                            torrent_hashes=self.ext_hash
                        )
                        if len(tor_info) > 0:
                            break
            else:
                sendMessage(
                    "Ini adalah tautan yang tidak didukung/tidak valid.",
                    listener.bot,
                    listener.update,
                )
                return
            gid = ''.join(
                random.SystemRandom().choices(
                    string.ascii_letters + string.digits, k=14
                )
            )
            with download_dict_lock:
                download_dict[listener.uid] = QbDownloadStatus(gid, listener, self.ext_hash, self.client)
            tor_info = tor_info[0]
            LOGGER.info(f"QbitDownload started: {tor_info.name}")
            self.updater = setInterval(self.update_interval, self.update)
            if BASE_URL is not None and qbitsel:
                if not is_file:
                    meta = sendMessage("Mengunduh metadata ... Harap tunggu maka Anda dapat memilih file atau mencerminkan file torrent jika memiliki seeder rendah", listener.bot, listener.update)
                    while True:
                            tor_info = self.client.torrents_info(torrent_hashes=self.ext_hash)
                            if len(tor_info) == 0:
                                deleteMessage(listener.bot, meta)
                                return False
                            try:
                                tor_info = tor_info[0]
                                if tor_info.state == "metaDL" or tor_info.state == "checkingResumeData":
                                    time.sleep(0.5)
                                else:
                                    time.sleep(2)
                                    deleteMessage(listener.bot, meta)
                                    break
                            except:
                                deleteMessage(listener.bot, meta)
                                return False
                self.client.torrents_pause(torrent_hashes=self.ext_hash)
                for n in str(self.ext_hash):
                    if n.isdigit():
                        pincode += str(n)
                        count += 1
                    if count == 4:
                        break
                URL = f'{BASE_URL}/slam/files/{self.ext_hash}'
                pindata = f"pin {gid} {pincode}"
                donedata = f"done {gid} {self.ext_hash}"
                buttons = button_build.ButtonMaker()
                buttons.buildbutton("Pilih File", URL)
                buttons.sbutton("Pincode", pindata)
                buttons.sbutton("Selesai memilih", donedata)
                QBBUTTONS = InlineKeyboardMarkup(buttons.build_menu(2))
                msg = "Unduhan Anda dijeda.Pilih file lalu tekan tombol Selesai Selesai untuk mulai mengunduh."
                sendMarkup(msg, listener.bot, listener.update, QBBUTTONS)
            else:
                sendStatusMessage(listener.update, listener.bot)
        except qba.UnsupportedMediaType415Error as e:
            LOGGER.error(str(e))
            sendMessage(
                "Ini adalah tautan yang tidak didukung/tidak valid. {str(e)}",
                listener.bot,
                listener.update,
            )
        except Exception as e:
            LOGGER.error(str(e))
            sendMessage(str(e), listener.bot, listener.update)
            self.client.torrents_delete(torrent_hashes=self.ext_hash, delete_files=True)

    def update(self):  # sourcery no-metrics
        tor_info = self.client.torrents_info(torrent_hashes=self.ext_hash)
        if len(tor_info) == 0:
            self.updater.cancel()
            return
        try:
            tor_info = tor_info[0]
            if tor_info.state == "metaDL":
                self.stalled_time = time.time()
                if time.time() - self.meta_time >= 600:
                    self.listener.onDownloadError("Dead Torrent!")
                    self.client.torrents_delete(torrent_hashes=self.ext_hash, delete_files=True)
                    self.updater.cancel()
                    return
            elif tor_info.state == "downloading":
                self.stalled_time = time.time()
                if (TORRENT_DIRECT_LIMIT is not None or TAR_UNZIP_LIMIT is not None) and not self.checked:
                    if self.listener.isTar or self.listener.extract:
                        is_tar_ext = True
                        mssg = f'Batas tar/unzip adalah {TAR_UNZIP_LIMIT}'
                    else:
                        is_tar_ext = False
                        mssg = f'Batas torrent/direct adalah {TORRENT_DIRECT_LIMIT}'
                    size = tor_info.size
                    result = check_limit(size, TORRENT_DIRECT_LIMIT, TAR_UNZIP_LIMIT, is_tar_ext)
                    self.checked = True
                    if result:
                        self.listener.onDownloadError(f"{mssg}.\nYour File/Folder size is {get_readable_file_size(size)}")
                        self.client.torrents_delete(torrent_hashes=self.ext_hash, delete_files=True)
                        self.updater.cancel()
                        return
            elif tor_info.state == "stalledDL":
                if time.time() - self.stalled_time >= 900:
                    self.listener.onDownloadError("Dead Torrent!")
                    self.client.torrents_delete(torrent_hashes=self.ext_hash, delete_files=True)
                    self.updater.cancel()
                    return
            elif tor_info.state == "error":
                self.listener.onDownloadError("Error. IDK why, report in support group")
                self.client.torrents_delete(torrent_hashes=self.ext_hash, delete_files=True)
                self.updater.cancel()
                return
            elif tor_info.state == "uploading" or tor_info.state.lower().endswith("up"):
                self.client.torrents_pause(torrent_hashes=self.ext_hash)
                if self.qbitsel:
                    for dirpath, subdir, files in os.walk(f"{self.dire}", topdown=False):
                        for file in files:
                            if fnmatch(file, "*.!qB"):
                                os.remove(os.path.join(dirpath, file))
                        for folder in subdir:
                            if fnmatch(folder, ".unwanted"):
                                shutil.rmtree(os.path.join(dirpath, folder))
                        if not os.listdir(dirpath):
                            os.rmdir(dirpath)
                self.listener.onDownloadComplete()
                self.client.torrents_delete(torrent_hashes=self.ext_hash, delete_files=True)
                self.updater.cancel()
        except:
            self.updater.cancel()


def get_confirm(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    data = data.split(" ")
    qdl = getDownloadByGid(data[1])
    if qdl is not None:
        if user_id != qdl.listener.message.from_user.id:
            query.answer(text="Jangan buang waktu Anda!", show_alert=True)
            return
        if data[0] == "pin":
            query.answer(text=data[2], show_alert=True)
        elif data[0] == "done":
            query.answer()
            qdl.client.torrents_resume(torrent_hashes=data[2])
            sendStatusMessage(qdl.listener.update, qdl.listener.bot)
            query.message.delete()
    else:
        query.answer(text="Tugas ini telah dibatalkan!", show_alert=True)
        query.message.delete()


def get_hash_magnet(mgt):
    if mgt.startswith('magnet:'):
        _, _, _, _, query, _ = urlparse(mgt)

    qs = parse_qs(query)
    v = qs.get('xt', None)

    if v is None or v == []:
        LOGGER.error('Invalid magnet URI: no "xt" query parameter.')
        return False

    v = v[0]
    if not v.startswith('urn:btih:'):
        LOGGER.error('Invalid magnet URI: "xt" value not valid for BitTorrent.')
        return False

    mgt = v[len('urn:btih:'):]
    return mgt.lower()


def get_hash_file(path):
    tr = Torrent.from_file(path)
    mgt = tr.magnet_link
    return get_hash_magnet(mgt)


pin_handler = CallbackQueryHandler(get_confirm, pattern="pin", run_async=True)
done_handler = CallbackQueryHandler(get_confirm, pattern="done", run_async=True)
dispatcher.add_handler(pin_handler)
dispatcher.add_handler(done_handler)
