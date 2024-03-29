import os
import sys

from discord import TextChannel, ClientUser
from discord.ext import commands, tasks
from loguru import logger

from alarm import AlarmMan


class EidolonBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        logger.info(f"{self.user} | Ready!")

        alarm_channel_id = os.getenv("ALARM_CHANNEL").split(",")
        alarm_channel_id = set(list(map(int, alarm_channel_id)))

        channels = list()
        for channel in self.get_all_channels():
            if channel.id in alarm_channel_id:
                channels.append(channel)
        self.add_cog(MasterCog(self, channels))


class MasterCog(commands.Cog):
    def __init__(self, bot: EidolonBot, channels):
        self.bot = bot
        self.am = AlarmMan()
        for channel in channels:
            ChannelAlarm(channel, self.bot.user, self.am)
        self.do_task.start()

    def cog_unload(self):
        self.do_task.cancel()

    @tasks.loop(seconds=300)
    async def do_task(self):
        logger.info("Refresh")
        self.am.refresh()


class ChannelAlarm(commands.Cog):
    def __init__(self, channel: TextChannel, user: ClientUser, am: AlarmMan):
        self.channel = channel
        self.user = user
        self.am = am
        self.do_task.start()

    def cog_unload(self):
        self.do_task.cancel()

    @tasks.loop(seconds=60)
    async def do_task(self):
        if self.channel.last_message_id is None:
            await self.channel.send(self.am.full_message())

        msg = await self.channel.fetch_message(self.channel.last_message_id)
        if msg.author == self.user:
            try:
                full_msg = self.am.full_message()
                if msg.content != full_msg:
                    await msg.edit(content=full_msg)
                    logger.info(f"Edit {self.channel}")
            except Exception as e:
                logger.error(f"Error: {str(e)}")

    def __repr__(self) -> str:
        return f"ChannelAlarm({self.user}, {self.channel})"


def set_logger():
    log_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSSSSS} | <lvl>{level: ^9}</lvl> | {message}"
    )
    logger.add(sys.stderr, level="INFO", format=log_format)
    logger.add(
        f"logs/bot.log",
        rotation="1 day",
        retention="7 days",
        level="INFO",
        encoding="UTF-8",
        compression="gz",
        format=log_format,
    )


if __name__ == "__main__":
    set_logger()
    token = os.getenv("TOKEN")
    EidolonBot(command_prefix="!").run(token)
