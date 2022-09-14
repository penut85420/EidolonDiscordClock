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
        self.channels = channels
        self.cogs = list()
        self.do_task.start()

    def cog_unload(self):
        self.do_task.cancel()

    @tasks.loop(seconds=30)
    async def do_task(self):
        logger.info("Cog Reset")
        for cog in self.cogs:
            logger.info(f"Remove {cog}")
            cog.cog_unload()
            self.bot.remove_cog(cog)
        self.cogs.clear()

        for channel in self.channels:
            cog = ChannelAlarm(channel, self.bot.user)
            logger.info(f"Add {cog}")
            self.bot.add_cog(cog)
            self.cogs.append(cog)


class ChannelAlarm(commands.Cog):
    RESET = 10

    def __init__(self, channel: TextChannel, user: ClientUser):
        self.channel = channel
        self.user = user
        self.am = AlarmMan()
        self.do_task.start()
        self.reset = ChannelAlarm.RESET

    def cog_unload(self):
        self.do_task.cancel()

    @tasks.loop(seconds=60)
    async def do_task(self):
        if self.channel.last_message_id is None:
            await self.channel.send(self.am.full_message())

        msg = await self.channel.fetch_message(self.channel.last_message_id)
        if msg.author == self.user:
            try:
                if msg.content != self.am.full_message():
                    await msg.edit(content=self.am.full_message())
                    logger.info(f"Edit {self.channel}")

                self.reset -= 1
                if self.reset <= 0:
                    logger.info(self.am.refresh())
                    self.reset = ChannelAlarm.RESET
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
