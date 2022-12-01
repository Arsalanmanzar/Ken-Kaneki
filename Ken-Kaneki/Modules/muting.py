import html
from typing import Optional
import html
from typing import Optional

from telegram import Bot, Chat, ChatPermissions, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler
from telegram.utils.helpers import mention_html
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from Bestie_Robot import LOGGER, TIGERS, dispatcher, DEMONS
from Bestie_Robot.modules.helper_funcs.chat_status import (
    bot_admin,
    can_restrict,
    connection_status,
    is_user_admin,
)

from Bestie_Robot.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from Bestie_Robot.modules.helper_funcs.string_handling import extract_time
from Bestie_Robot.modules.log_channel import loggable
from telegram import Bot, Chat, ChatPermissions, ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, run_async
from telegram.utils.helpers import mention_html
from Bestie_Robot.modules.helper_funcs.xyz import igrisxcallback

from Bestie_Robot.modules.helper_funcs.anonymous import user_admin, AdminPerms


def check_user(user_id: int, bot: Bot, chat: Chat) -> Optional[str]:
    if not user_id:
        reply = "You don't seem to be referring to a user or the ID specified is incorrect.."
        return reply

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            reply = "I can't seem to find this user"
            return reply
        else:
            raise

    if user_id == bot.id:
        reply = "I'm not gonna MUTE myself, How high are you?"
        return reply

    if is_user_admin(chat, user_id, member) or user_id in TIGERS or user_id in DEMONS:
        reply = "Can't. Find someone else to mute but not this one."
        return reply

    return None


@connection_status
@bot_admin
@user_admin(AdminPerms.CAN_RESTRICT_MEMBERS)
@loggable
def mute(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id, reason = extract_user_and_text(message, args)
    reply = check_user(user_id, bot, chat)

    if reply:
        message.reply_text(reply)
        return ""

    member = chat.get_member(user_id)

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#MUTE\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    if reason:
        log += f"\n<b>Reason:</b> {reason}"

    if member.can_send_messages is None or member.can_send_messages:
        chat_permissions = ChatPermissions(can_send_messages=False)
        bot.restrict_chat_member(chat.id, user_id, chat_permissions)
        reply = (
            f"❗<b>Muted</b>\n"
            f"<b>➣ User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
            f"<b>➣ Muted for: no expiration date</b>"
        )
        if reason:
            reply += f"\n<b>➣ Reason:</b> {reason}"
        bot.sendMessage(
            chat.id,
            reply,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Unmute", callback_data=f"mute_mute={user_id}"
                        ),
                        InlineKeyboardButton(text="Delete", callback_data="mute_del"),
                    ]
                ]
            ),
            parse_mode=ParseMode.HTML,
        )
        return log

    else:
        message.reply_text("This user is already muted!")

    return ""


@connection_status
@bot_admin
@user_admin(AdminPerms.CAN_RESTRICT_MEMBERS)
@loggable
def unmute(update: Update, context: CallbackContext) -> str:
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "You'll need to either give me a username to unmute, or reply to someone to be unmuted.",
        )
        return ""

    member = chat.get_member(int(user_id))

    if member.status != "kicked" and member.status != "left":
        if (
            member.can_send_messages
            and member.can_send_media_messages
            and member.can_send_other_messages
            and member.can_add_web_page_previews
        ):
            message.reply_text("This user already has the right to speak.")
        else:
            chat_permissions = ChatPermissions(
                can_send_messages=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_send_polls=True,
                can_change_info=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
            try:
                bot.restrict_chat_member(chat.id, int(user_id), chat_permissions)
            except BadRequest:
                pass
            bot.sendMessage(
                chat.id,
                f"I shall allow <b>{html.escape(member.user.first_name)}</b> to text!",
                parse_mode=ParseMode.HTML,
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#UNMUTE\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
            )
    else:
        message.reply_text(
            "This user isn't even in the chat, unmuting them won't make them talk more than they "
            "already do!",
        )

    return ""


@connection_status
@bot_admin
@can_restrict
@user_admin(AdminPerms.CAN_RESTRICT_MEMBERS)
@loggable
def temp_mute(update: Update, context: CallbackContext) -> str:
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id, reason = extract_user_and_text(message, args)
    reply = check_user(user_id, bot, chat)

    if reply:
        message.reply_text(reply)
        return ""

    member = chat.get_member(user_id)

    if not reason:
        message.reply_text("You haven't specified a time to mute this user for!")
        return ""

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    if len(split_reason) > 1:
        reason = split_reason[1]
    else:
        reason = ""

    mutetime = extract_time(message, time_val)

    if not mutetime:
        return ""

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#TEMP MUTED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}\n"
        f"<b>Time:</b> {time_val}"
    )
    if reason:
        log += f"\n<b>Reason:</b> {reason}"

    try:
        if member.can_send_messages is None or member.can_send_messages:
            chat_permissions = ChatPermissions(can_send_messages=False)
            bot.restrict_chat_member(
                chat.id,
                user_id,
                chat_permissions,
                until_date=mutetime,
            )
            reply_msg = (
                f"❗<b>Time Muted</b>\n"
                f"<b>➣ User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
                f"<b>➣ Muted for: {time_val}</b>"
            )
            bot.sendMessage(
                chat.id,
                reply_msg,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Unmute", callback_data=f"mute_mute={user_id}"
                            ),
                            InlineKeyboardButton(
                                text="Delete", callback_data="mute_del"
                            ),
                        ]
                    ]
                ),
                parse_mode=ParseMode.HTML,
            )
            return log

        else:
            message.reply_text("This user is already muted.")

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text(f"Muted for {time_val}!", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR muting user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Well damn, I can't mute that user.")

    return ""


@igrisxcallback(pattern=r"mute_")
@connection_status
@bot_admin
@loggable
def mute_callback(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    query = update.callback_query
    chat = update.effective_chat
    user = update.effective_user
    if query.data != "mute_del":
        splitter = query.data.split("=")
        query_match = splitter[0]
        if query_match == "mute_mute":
            user_id = splitter[1]
            if not is_user_admin(chat, int(user.id)):
                bot.answer_callback_query(
                    query.id,
                    text="You don't have enough rights to unmute people",
                    show_alert=True,
                )
                return ""
            member = chat.get_member(int(user_id))

            if member.status not in ("kicked", "left"):
                if (
                    member.can_send_messages
                    and member.can_send_media_messages
                    and member.can_send_other_messages
                    and member.can_add_web_page_previews
                ):
                    query.message.edit_text("This user already has the right to text.")
                else:
                    chat_permissions = ChatPermissions(
                        can_send_messages=True,
                        can_invite_users=True,
                        can_pin_messages=True,
                        can_send_polls=True,
                        can_change_info=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True,
                    )
                try:
                    bot.restrict_chat_member(chat.id, int(user_id), chat_permissions)
                except BadRequest:
                    pass
                query.message.edit_text(
                    f"I shall allow <b>{html.escape(member.user.first_name)}</b> to text!",
                    parse_mode=ParseMode.HTML,
                )
                bot.answer_callback_query(query.id, text="Unmuted this user")
                return (
                    f"<b>{html.escape(chat.title)}:</b>\n"
                    f"#UNMUTE\n"
                    f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                    f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
                )

    else:
        if not is_user_admin(chat, int(user.id)):
            bot.answer_callback_query(
                query.id,
                text="You don't have enough rights to delete this message.",
                show_alert=True,
            )
            return ""
        query.message.delete()
        bot.answer_callback_query(query.id, text="Deleted!")
        return ""


__help__ = """
*Admins only:*
➢ `/mute <userhandle>`*:* silences a user. Can also be used as a reply, muting the replied to user.
➢ `/tmute <userhandle> x(m/h/d)`*:* mutes a user for x time. (via handle, or reply). `m` = `minutes`, `h` = `hours`, `d` = `days`.
➢ `/unmute <userhandle>`*:* unmutes a user. Can also be used as a reply, muting the replied to user.
"""

MUTE_HANDLER = CommandHandler("mute", mute, run_async=True)
UNMUTE_HANDLER = CommandHandler("unmute", unmute, run_async=True)
TEMPMUTE_HANDLER = CommandHandler(["tmute", "tempmute"], temp_mute, run_async=True)

dispatcher.add_handler(MUTE_HANDLER)
dispatcher.add_handler(UNMUTE_HANDLER)
dispatcher.add_handler(TEMPMUTE_HANDLER)

__mod_name__ = "Muting"
__handlers__ = [MUTE_HANDLER, UNMUTE_HANDLER, TEMPMUTE_HANDLER]
