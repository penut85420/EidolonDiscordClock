import os
import sys
import asyncio
import discord

from loguru import logger
from alarm import AlarmMan

class EidolonBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        log(f'{self.user} | Ready!')

        reset = 1000
        am = AlarmMan()
        alarm_channel_id = int(os.getenv('ALARM_CHANNEL'))

        for channel in self.get_all_channels():
            if channel.id == alarm_channel_id:
                if channel.last_message_id is None:
                    await channel.send(am.full_message())

                msg = await channel.fetch_message(channel.last_message_id)
                if msg.author == self.user:
                    while not self.is_closed():
                        try:
                            if msg.content != am.full_message():
                                await msg.edit(content=am.full_message())

                            await asyncio.sleep(3)

                            reset -= 1
                            if reset < 0:
                                log(am.refresh())
                                reset = 1000
                        except Exception as e:
                            logger.error(f'Error: {str(e)}')

    async def on_message(self, msg):
        if msg.author == self.user:
            return

def set_logger():
    log_format = (
        '{time:YYYY-MM-DD HH:mm:ss.SSSSSS} | '
        '<lvl>{level: ^9}</lvl> | '
        '{message}'
    )
    logger.add(sys.stderr, level='INFO', format=log_format)
    logger.add(
        f'./logs/bot.log',
        rotation='7 day',
        retention='30 days',
        level='INFO',
        encoding='UTF-8',
        format=log_format
    )

def log(msg):
    logger.info(msg)

if __name__ == '__main__':
    set_logger()
    token = os.environ['TOKEN']
    EidolonBot().run(token)
