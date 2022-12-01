from Bestie_Robot import pbot
from pyrogram import filters
from pyrogram.types import Message
import asyncio
import io


@pbot.on_message(filters.command("(term|terminal|sh|shell)", prefixes=["/", ".", "?", "-"]))
async def shell(_, m: Message):
    cmd = m.command
    if len(cmd) == 1:
        return
    else:
        cmd = cmd[1]
    async_process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await async_process.communicate()
    msg = ""
    if stderr.decode():
        msg += f"**#STDERR:**\n`{stderr.decode()}`"
    if stdout.decode():
        msg += f"**#STDOUT:**\n`{stdout.decode()}`"
    if len(msg) > 4096:
        with io.BytesIO(msg) as file:
            file.name = "shell.txt"
                await pbot.send_file(
                m.chat.id,
                file,
                force_document=True,
                caption="`Output Was Too Long, Sent As File`",
            )
            return
    await m.reply_text(msg)
