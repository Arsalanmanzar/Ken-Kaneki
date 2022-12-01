from Bestie_Robot import pbot
from pyrogram import filters
from pyrogram.types import Message

@pbot.on_message(filters.command("whois", prefixes=["/", ".", "?", "-"]))
async def whois(_, m: Message):
    if m.reply_to_message:
        user = m.reply_to_message.from_user.id
    elif not m.reply_to_message and len(m.command) == 1:
        user = m.from_user.id
    elif not m.reply_to_message and len(m.command) != 1:
        user = m.text.split(None, 1)[1]
        return
    try:
        data = await pbot.get_users(user)
        boom = await pbot.get_chat(user)
    except Exception as e:
        await m.reply_photo("https://c4.wallpaperflare.com/wallpaper/976/117/318/anime-girls-404-not-found-glowing-eyes-girls-frontline-wallpaper-preview.jpg", caption=f"`404 Error Occurred Failed To Get Data Of The User`\n\n `{e}`")
        return
    await pbot.send_message(
        m.chat.id,
        f"**╒═══「 Appraisal Results: 」**\n**➛ First Name:** `{data.first_name}`\n**➛ Last Name:** `{data.last_name}`\n**➛ Username: @{data.username}**\n**➛ Userlink: {data.mention}**\n**➛ User ID:** `{data.id}`\n**➛ About:** `{boom.bio}`",
    )
