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
            msg1 = sendMessage(f"Memeriksa Tautan Anda...", context.bot, update)
            res, clonesize, name = gd.clonehelper(link)
            if res != "":
               deleteMessage(context.bot, msg1)
               sendMessage(res, context.bot, update)
               return
            if STOP_DUPLICATE_CLONE:
                LOGGER.info(f"Memeriksa File/Folder jika sudah di Drive...")
                smsg, button = gd.drive_list(name)
                if smsg:
                    deleteMessage(context.bot, msg1)
                    msg3 = "File/Folder sudah tersedia di Drive.\nBerikut adalah hasil pencariannya:"
                    sendMarkup(msg3, context.bot, update, button)
                    return
                else:
                    if CLONE_LIMIT is None:
                        deleteMessage(context.bot, msg1)
            if CLONE_LIMIT is not None:
                LOGGER.info(f"Checking File/Folder Size...")
                limit = CLONE_LIMIT
                limit = limit.split(' ', maxsplit=1)
                limitint = int(limit[0])
                msg2 = f'Gagal, batas Klon adalah {CLONE_LIMIT}.\nSementara FIle/folder kamu ukurannya sebesar {get_readable_file_size(clonesize)}.'
                if 'GB' in limit or 'gb' in limit:
                    if clonesize > limitint * 1024**3:
                        deleteMessage(context.bot, msg1)
                        sendMessage(msg2, context.bot, update)
                        return
                    else:
                        deleteMessage(context.bot, msg1)
                elif 'TB' in limit or 'tb' in limit:
                    if clonesize > limitint * 1024**4:
                        deleteMessage(context.bot, msg1)
                        sendMessage(msg2, context.bot, update)
                        return
                    else:
                        deleteMessage(context.bot, msg1)                
        msg = sendMessage(f"Klon: <code>{link}</code>", context.bot, update)
        result, button = gd.clone(link)
        deleteMessage(context.bot, msg)
        if button == "":
            sendMessage(result, context.bot, update)
        else:
            if update.message.from_user.username:
                uname = f'@{update.message.from_user.username}'
            else:
                uname = f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}</a>'
            if uname is not None:
                cc = f'\n\ncc: {uname}'
            sendMarkup(result + cc, context.bot, update, button)
    else:
        sendMessage('Provide G-Drive Shareable Link to Clone.', context.bot, update)

clone_handler = CommandHandler(BotCommands.CloneCommand, cloneNode, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(clone_handler)
