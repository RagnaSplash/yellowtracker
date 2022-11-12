import logging
from yellowtracker.domain.bot import Bot
from yellowtracker.domain.track_type import TrackType
from yellowtracker.service.channel_service import ChannelService
from yellowtracker.util.track_util import TrackUtil

log = logging.getLogger(__name__)

class TrackTimer:

    @staticmethod
    async def timer(bot: Bot):
        if not bot.tracker_ready:
            return
        for guild in bot.guilds:
            guild_state = bot.guild_state_map.get(guild.id)
            if guild_state is None:
                continue
            for id_channel in guild_state['channel_state_map'].copy():
                channel_state = guild_state['channel_state_map'].get(id_channel)
                if channel_state is None:
                    continue
                track_type = channel_state['type']
                cmp = 'r2' if track_type == TrackType.MVP else 'r1'
                has_active_entries = False
                for entry_state in channel_state['entry_state_list']:
                    TrackUtil.calc_remaining_time(entry_state, entry_state['track_time'], channel_state['type'])
                    if not has_active_entries and entry_state[cmp] > -bot.TABLE_ENTRY_EXPIRATION_MINS:
                        has_active_entries = True
                if has_active_entries:
                    await ChannelService.update_channel_message(bot, channel_state)
                channel = ChannelService.get_channel_from_guild(guild, channel_state['id_channel'])
                if channel is None:
                    continue
                if ChannelService.validate_channel(bot, channel) is not None:
                    continue
                await ChannelService.delete_msgs(bot, channel_state, channel)
