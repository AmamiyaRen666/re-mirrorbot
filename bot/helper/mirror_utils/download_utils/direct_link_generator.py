# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Helper Module containing various sites direct links generators. This module is copied and modified as per need
from https://github.com/AvinashReddy3108/PaperplaneExtended . I hereby take no credit of the following code other
than the modifications. See https://github.com/AvinashReddy3108/PaperplaneExtended/commits/master/userbot/modules/direct_links.py
for original authorship. """

import json
import math
import re
import urllib.parse
from base64 import standard_b64encode
from os import popen
from random import choice
from urllib.parse import urlparse

import cloudscraper
import lk21
import requests
from bs4 import BeautifulSoup
from js2py import EvalJs
from lk21.extractors.bypasser import Bypass

from bot import LOGGER, UPTOBOX_TOKEN
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException
from bot.helper.telegram_helper.bot_commands import BotCommands


def direct_link_generator(link: str):  # sourcery no-metrics
    """ direct links generator """
    if not link:
        raise DirectDownloadLinkException("Tidak ditemukan tautan!")
    elif 'youtube.com' in link or 'youtu.be' in link:
        raise DirectDownloadLinkException(
            f"Gunakan /{BotCommands.WatchCommand} untuk mencerminkan tautan YouTube\nGunakan /{BotCommands.TarWatchCommand} Untuk membuat tar daftar putar YouTube"
        )
    elif 'zippyshare.com' in link:
        return zippy_share(link)
    elif 'yadi.sk' in link:
        return yandex_disk(link)
    elif 'mediafire.com' in link:
        return mediafire(link)
    elif 'uptobox.com' in link:
        return uptobox(link)
    elif 'osdn.net' in link:
        return osdn(link)
    elif 'github.com' in link:
        return github(link)
    elif 'hxfile.co' in link:
        return hxfile(link)
    elif 'anonfiles.com' in link:
        return anonfiles(link)
    elif 'letsupload.io' in link:
        return letsupload(link)
    elif 'fembed.net' in link:
        return fembed(link)
    elif 'fembed.com' in link:
        return fembed(link)
    elif 'femax20.com' in link:
        return fembed(link)
    elif 'fcdn.stream' in link:
        return fembed(link)
    elif 'feurl.com' in link:
        return fembed(link)
    elif 'naniplay.nanime.in' in link:
        return fembed(link)
    elif 'naniplay.nanime.biz' in link:
        return fembed(link)
    elif 'naniplay.com' in link:
        return fembed(link)
    elif 'layarkacaxxi.icu' in link:
        return fembed(link)
    elif 'sbembed.com' in link:
        return sbembed(link)
    elif 'streamsb.net' in link:
        return sbembed(link)
    elif 'sbplay.org' in link:
        return sbembed(link)
    elif '1drv.ms' in link:
        return onedrive(link)
    elif 'pixeldrain.com' in link:
        return pixeldrain(link)
    elif 'antfiles.com' in link:
        return antfiles(link)
    elif 'streamtape.com' in link:
        return streamtape(link)
    elif 'bayfiles.com' in link:
        return anonfiles(link)
    elif 'racaty.net' in link:
        return racaty(link)
    elif '1fichier.com' in link:
        return fichier(link)
    elif 'https://sourceforge.net' in link:
        return sourceforge(link)
    elif 'https://master.dl.sourceforge.net' in link:
        return mastersource(link)
    elif 'solidfiles.com' in link:
        return solidfiles(link)
    else:
        raise DirectDownloadLinkException(
            f'No Direct link function found for {link}'
        )


def zippy_share(url: str) -> str:
    """ ZippyShare direct links generator
    Based on https://github.com/KenHV/Mirror-Bot
             https://github.com/jovanzers/WinTenCermin """
    try:
        link = re.findall(r'\bhttps?://.*zippyshare\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No Zippyshare links found")
    try:
        base_url = re.search('http.+.zippyshare.com', link).group()
        response = requests.get(link).content
        pages = BeautifulSoup(response, "lxml")
        try:
            js_script = pages.find("div", {
                "class": "center"
            }).find_all("script")[1]
        except IndexError:
            js_script = pages.find("div", {
                "class": "right"
            }).find_all("script")[0]
        js_content = re.findall(r'\.href.=."/(.*?)";', str(js_script))
        js_content = 'var x = "/' + js_content[0] + '"'
        evaljs = EvalJs()
        setattr(evaljs, "x", None)
        evaljs.execute(js_content)
        js_content = getattr(evaljs, "x")
        return base_url + js_content
    except IndexError:
        raise DirectDownloadLinkException("ERROR: Tidak dapat menemukan tombol Unduh")

def yandex_disk(url: str) -> str:
    """ Yandex.Disk direct links generator
    Based on https://github.com/wldhx/yadisk-direct """
    try:
        link = re.findall(r'\bhttps?://.*yadi\.sk\S+', url)[0]
    except IndexError:
        return "No Yandex.Disk links found\n"
    api = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={}'
    try:
        return requests.get(api.format(link)).json()['href']
    except KeyError:
        raise DirectDownloadLinkException("ERROR: File not found/Download limit reached\n")

def sourceforge(url: str) -> str:
    """ SourceForge direct links generator
    Based on https://github.com/REBEL75/REBELUSERBOT """
    try:
        link = re.findall(r"\bhttps?://sourceforge\.net\S+", url)[0]
    except IndexError:
        return "`No SourceForge links found`\n"
    file_path = re.findall(r"files(.*)/download", link)[0]
    project = re.findall(r"projects?/(.*?)/files", link)[0]
    mirrors = (
        f"https://sourceforge.net/settings/mirror_choices?"
        f"projectname={project}&filename={file_path}"
    )
    page = BeautifulSoup(requests.get(mirrors).content, "html.parser")
    info = page.find("ul", {"id": "mirrorList"}).findAll("li")
    for mirror in info[1:]:
        name = re.findall(r"\((.*)\)", mirror.text.strip())[0]
        dl_url = (
            f'https://{mirror["id"]}.dl.sourceforge.net/project/{project}/{file_path}'
        )
    return dl_url

def uptobox(url: str) -> str:
    """ Uptobox direct links generator
    based on https://github.com/jovanzers/WinTenCermin """
    try:
        link = re.findall(r'\bhttps?://.*uptobox\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("Tidak ditemukan tautan uptobox\n")
    if UPTOBOX_TOKEN is None:
        LOGGER.error('UPTOBOX_TOKEN tidak tersedia!')
        dl_url = link
    else:
        try:
            link = re.findall(r'\bhttp?://.*uptobox\.com/dl\S+', url)[0]
            dl_url = link
        except:
            file_id = re.findall(r'\bhttps?://.*uptobox\.com/(\w+)', url)[0]
            file_link = 'https://uptobox.com/api/link?token={}&file_code={}'.format(
                UPTOBOX_TOKEN, file_id)
            req = requests.get(file_link)
            result = req.json()
            dl_url = result['data']['dlLink']
    return dl_url


def mediafire(url: str) -> str:
    """ MediaFire direct links generator """
    try:
        link = re.findall(r'\bhttps?://.*mediafire\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("Tidak ditemukan tautan mediafire\n")
    page = BeautifulSoup(requests.get(link).content, 'lxml')
    info = page.find('a', {'aria-label': 'Download file'})
    return info.get('href')


def osdn(url: str) -> str:
    """ OSDN direct links generator """
    osdn_link = 'https://osdn.net'
    try:
        link = re.findall(r'\bhttps?://.*osdn\.net\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("Tidak ditemukan tautan OSDN\n")
    page = BeautifulSoup(
        requests.get(link, allow_redirects=True).content, 'lxml'
    )
    info = page.find('a', {'class': 'mirror_link'})
    link = urllib.parse.unquote(osdn_link + info['href'])
    mirrors = page.find('form', {'id': 'mirror-select-form'}).findAll('tr')
    urls = []
    for data in mirrors[1:]:
        mirror = data.find('input')['value']
        urls.append(re.sub(r'm=(.*)&f', f'm={mirror}&f', link))
    return urls[0]


def github(url: str) -> str:
    """ GitHub direct links generator """
    try:
        re.findall(r'\bhttps?://.*github\.com.*releases\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("Tidak ada tautan rilis github yang ditemukan\n")
    download = requests.get(url, stream=True, allow_redirects=False)
    try:
        return download.headers["location"]
    except KeyError:
        raise DirectDownloadLinkException("ERROR: Tidak dapat mengekstrak tautan\n")


def hxfile(url: str) -> str:
    """ Hxfile direct link generator
    Based on https://github.com/zevtyardt/lk21
             https://github.com/breakdowns/slam-aria-mirror-bot """
    bypasser = lk21.Bypass()
    return bypasser.bypass_filesIm(url)


def anonfiles(url: str) -> str:
    """ Anonfiles direct link generator
    Based on https://github.com/zevtyardt/lk21
             https://github.com/breakdowns/slam-aria-mirror-bot """
    bypasser = lk21.Bypass()
    return bypasser.bypass_anonfiles(url)


def letsupload(url: str) -> str:
    """ Letsupload direct link generator
    Based on https://github.com/zevtyardt/lk21
             https://github.com/breakdowns/slam-aria-mirror-bot """
    dl_url = ''
    try:
        link = re.findall(r'\bhttps?://.*letsupload\.io\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("Tidak ada tautan letsupload yang ditemukan\n")
    bypasser = lk21.Bypass()
    dl_url = bypasser.bypass_url(link)
    return dl_url


def fembed(link: str) -> str:
    """ Fembed direct link generator
    Based on https://github.com/zevtyardt/lk21
             https://github.com/breakdowns/slam-aria-mirror-bot """
    bypasser = lk21.Bypass()
    dl_url = bypasser.bypass_fembed(link)
    count = len(dl_url)
    lst_link = [dl_url[i] for i in dl_url]
    return lst_link[count - 1]


def sbembed(link: str) -> str:
    """ Sbembed direct link generator
    Based on https://github.com/zevtyardt/lk21
             https://github.com/breakdowns/slam-aria-mirror-bot """
    bypasser = lk21.Bypass()
    dl_url = bypasser.bypass_sbembed(link)
    count = len(dl_url)
    lst_link = [dl_url[i] for i in dl_url]
    return lst_link[count - 1]


def onedrive(link: str) -> str:
    """ Onedrive direct link generator
    Based on https://github.com/UsergeTeam/Userge """
    link_without_query = urlparse(link)._replace(query=None).geturl()
    direct_link_encoded = str(
        standard_b64encode(bytes(link_without_query, "utf-8")), "utf-8"
    )
    direct_link1 = f"https://api.onedrive.com/v1.0/shares/u!{direct_link_encoded}/root/content"
    resp = requests.head(direct_link1)
    if resp.status_code != 302:
        return "ERROR: Tautan tidak sah, tautannya mungkin pribadi"
    dl_link = resp.next.url
    file_name = dl_link.rsplit("/", 1)[1]
    resp2 = requests.head(dl_link)
    return dl_link


def pixeldrain(url: str) -> str:
    """ Based on https://github.com/yash-dk/TorToolkit-Telegram """
    url = url.strip("/ ")
    file_id = url.split("/")[-1]
    info_link = f"https://pixeldrain.com/api/file/{file_id}/info"
    dl_link = f"https://pixeldrain.com/api/file/{file_id}"
    resp = requests.get(info_link).json()
    if resp["success"]:
        return dl_link
    else:
        raise DirectDownloadLinkException(
            "ERROR: Tidak dapat mengunduh karena {}.".format(resp.text["value"])
        )


def antfiles(url: str) -> str:
    """ Antfiles direct link generator
    Based on https://github.com/zevtyardt/lk21
             https://github.com/breakdowns/slam-aria-mirror-bot """
    bypasser = lk21.Bypass()
    return bypasser.bypass_antfiles(url)


def streamtape(url: str) -> str:
    """ Streamtape direct link generator
    Based on https://github.com/zevtyardt/lk21
             https://github.com/breakdowns/slam-aria-mirror-bot """
    bypasser = lk21.Bypass()
    return bypasser.bypass_streamtape(url)


def racaty(url: str) -> str:
    """ Racaty direct links generator
    based on https://github.com/breakdowns/slam-aria-mirror-bot """
    dl_url = ''
    try:
        link = re.findall(r'\bhttps?://.*racaty\.net\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("Tidak ada tautan racaty yang ditemukan\n")
    scraper = cloudscraper.create_scraper()
    r = scraper.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    op = soup.find("input", {"name": "op"})["value"]
    ids = soup.find("input", {"name": "id"})["value"]
    rpost = scraper.post(url, data={"op": op, "id": ids})
    rsoup = BeautifulSoup(rpost.text, "lxml")
    dl_url = rsoup.find("a",
                        {"id": "uniqueExpirylink"})["href"].replace(" ", "%20")
    return dl_url


def fichier(link: str) -> str:  # sourcery no-metrics
    """ 1Fichier direct links generator
    Based on https://github.com/Maujar
             https://github.com/breakdowns/slam-aria-mirror-bot """
    regex = r"^([http:\/\/|https:\/\/]+)?.*1fichier\.com\/\?.+"
    gan = re.match(regex, link)
    if not gan:
        raise DirectDownloadLinkException(
            "ERROR: Tautan yang Anda masukkan salah!"
        )
    if "::" in link:
        pswd = link.split("::")[-1]
        url = link.split("::")[-2]
    else:
        pswd = None
        url = link
    try:
        if pswd is None:
            req = requests.post(url)
        else:
            pw = {"pass": pswd}
            req = requests.post(url, data=pe)
    except BaseException:
        raise DirectDownloadLinkException(
            "ERROR: Tidak dapat mencapai server 1fichier!"
        )
    if req.status_code == 404:
      raise DirectDownloadLinkException("ERROR: File tidak ditemukan/tautan yang Anda masukkan salah!")
    soup = BeautifulSoup(req.content, 'lxml')
    if soup.find("a", {"class": "ok btn-general btn-orange"}) is not None:
        dl_url = soup.find("a", {"class": "ok btn-general btn-orange"})["href"]
        if dl_url is None:
            raise DirectDownloadLinkException(
                "ERROR: Tidak dapat menghasilkan tautan langsung 1fichier!"
            )
        else:
            return dl_url
    elif len(soup.find_all("div", {"class": "ct_warn"})) == 2:
        str_2 = soup.find_all("div", {"class": "ct_warn"})[-1]
        if "you must wait" in str(str_2).lower():
            numbers = [
                int(word) for word in str(str_2).split() if word.isdigit()
            ]
            if not numbers:
                raise DirectDownloadLinkException(
                    "ERROR: 1Fichier berada pada batas.Harap tunggu beberapa menit/jam."
                )
            else:
                raise DirectDownloadLinkException(
                    f"ERROR: 1fichier berada pada batas. Tunggu sebentar {numbers[0]} menit."
                )
        elif "protect access" in str(str_2).lower():
            raise DirectDownloadLinkException(
                "ERROR: Tautan ini memerlukan kata sandi!\n\n<b>Tautan ini memerlukan kata sandi!</b>\n- Insert sign <b>::</b> after the link and write the password after the sign.\n\n<b>Example:</b>\n<code>/mirror https://1fichier.com/?smmtd8twfpm66awbqz04::love you</code>\n\n* No spaces between the signs <b>::</b>\n* For the password, you can use a space!"
            )
        else:
            raise DirectDownloadLinkException(
                "ERROR: Kesalahan mencoba menghasilkan tautan langsung dari 1fichier!"
            )
    elif len(soup.find_all("div", {"class": "ct_warn"})) == 3:
        str_1 = soup.find_all("div", {"class": "ct_warn"})[-2]
        str_3 = soup.find_all("div", {"class": "ct_warn"})[-1]
        if "you must wait" in str(str_1).lower():
            numbers = [
                int(word) for word in str(str_1).split() if word.isdigit()
            ]
            if not numbers:
                raise DirectDownloadLinkException(
                    "ERROR: 1Fichier berada pada batas. Harap tunggu beberapa menit / jam."
                )
            else:
                raise DirectDownloadLinkException(
                    f"ERROR: 1fichier berada pada batas. Tunggu sebentar {numbers[0]} menit."
                )
        elif "bad password" in str(str_3).lower():
            raise DirectDownloadLinkException(
                "ERROR: Kata sandi yang Anda masukkan salah!"
            )
        else:
            raise DirectDownloadLinkException(
                "ERROR: Kesalahan mencoba menghasilkan tautan langsung dari 1fichier!"
            )


def solidfiles(url: str) -> str:
    """ Solidfiles direct links generator
    Based on https://github.com/Xonshiz/SolidFiles-Downloader
    By https://github.com/Jusidama18 """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    pageSource = requests.get(url, headers = headers).text
    mainOptions = str(re.search(r'viewerOptions\'\,\ (.*?)\)\;', pageSource).group(1))
    return json.loads(mainOptions)["downloadUrl"]

def mastersource(url: str) -> str:
    """ Sourceforge Master.dl bypass """
    return f"{url}" + "?viasf=1"

def useragent():
    """
    useragent random setter
    """
    useragents = BeautifulSoup(
        requests.get(
            'https://developers.whatismybrowser.com/'
            'useragents/explore/operating_system_name/android/'
        ).content, 'lxml'
    ).findAll('td', {'class': 'useragent'})
    user_agent = choice(useragents)
    return user_agent.text
