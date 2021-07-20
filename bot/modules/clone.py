from telegram.ext import CommandHandler
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.telegram_helper.message_utils import sendMarkup, deleteMessage, sendMessage
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot import dispatcher, LOGGER, CLONE_LIMIT, STOP_DUPLICATE_CLONE
from bot.helper.ext_utils.bot_utils import get_readable_file_size


def cloneNode(update, context):
    args = update.message.text.split(" ", maxsplit=1)
    if len(args) > 1:
        link = args[1]
        gd = GoogleDriveHelper()
        if CLONE_LIMIT is not None or STOP_DUPLICATE_CLONE:
            res, clonesize, name = gd.clonehelper(link)
            if res != "":
                sendMessage(res, context.bot, update)
                return
            if STOP_DUPLICATE_CLONE:
                LOGGER.info(f"Memeriksa File/Folder jika sudah di Drive...")
                smsg, button = gd.drive_list(name)
                if smsg:
                    msg3 = "File/folder sudah tersedia di drive.\nBerikut adalah hasil pencarian:"
                    sendMarkup(msg3, context.bot, update, button)
                    return
            if CLONE_LIMIT is not None:
                LOGGER.info(f"Memeriksa ukuran file/folder...")
                limit = CLONE_LIMIT
                limit = limit.split(' ', maxsplit=1)
                limitint = int(limit[0])
                msg2 = f'Gagal, batas klon adalah {CLONE_LIMIT}.\nUkuran file / folder Anda {get_readable_file_size(clonesize)}.'
                if 'G' in limit[1] or 'g' in limit[1]:
                    if clonesize > limitint * 1024**3:
                        sendMessage(msg2, context.bot, update)
                        return
                elif 'T' in limit[1] or 't' in limit[1]:
                    if clonesize > limitint * 1024**4:
                        sendMessage(msg2, context.bot, update)
                        return
        msg = sendMessage(f"Kloning: <code>{link}</code>", context.bot, update)
        result, button = gd.clone(link)
        deleteMessage(context.bot, msg)
        if button == "":
            sendMessage(result, context.bot, update)
        else:
            drive = gdriveTools.GoogleDriveHelper(name)
            gid = ''.join(
                random.SystemRandom().choices(
                    string.ascii_letters + string.digits, k=12
                )
            )
            clone_status = CloneStatus(drive, clonesize, update, gid)
            with download_dict_lock:
                download_dict[update.message.message_id] = clone_status
            if len(Interval) == 0:
                Interval.append(
                    setInterval(
                        DOWNLOAD_STATUS_UPDATE_INTERVAL, update_all_messages
                    )
                )
            sendStatusMessage(update, context.bot)
            result, button = drive.clone(link)
            with download_dict_lock:
                del download_dict[update.message.message_id]
                count = len(download_dict)
            try:
                if count == 0:
                    Interval[0].cancel()
                    del Interval[0]
                    delete_all_messages()
                else:
                    update_all_messages()
            except IndexError:
                pass
        if update.message.from_user.username:
            uname = f'@{update.message.from_user.username}'
        else:
            uname = f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}</a>'
        if uname is not None:
            cc = f'\n\nDari: {uname}'
            men = f'{uname} '
        if button == "cancelled" or button == "":
            sendMessage(men + result, context.bot, update)
        else:
            sendMarkup(result + cc, context.bot, update, button)
    else:
        sendMessage(
            'Provide G-Drive Shareable Link to Clone.', context.bot, update
        )


clone_handler = CommandHandler(
    BotCommands.CloneCommand,
    cloneNode,
    filters=CustomFilters.authorized_chat | CustomFilters.authorized_user,
    run_async=True
)
dispatcher.add_handler(clone_handler)
