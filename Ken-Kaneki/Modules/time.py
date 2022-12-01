from Bestie_Robot import pbot
from pyrogram import filters
from pyrogram.types import Message

@pbot.on_message(filters.command("when", prefixes=["/", ".", "?", "-"]))
async def when(_, m: Message):
    if m.reply_to_message:
        await pbot.send_message(m.reply_to_message.date)
        return
    if not m.reply_to_message:
        await pbot.send_message(m.date)
        return
