import numpy as np
from datetime import datetime
import re
import logging
import pytz
from .convert_timezone import convert_timezone


def get_game_times_from_post(pattern, message, dt_format, post_time, n_games):
    logger = logging.getLogger(__name__)
    end_times = re.findall(pattern, message)
    if end_times is None or end_times == []:
        logger.warning('Deadline timestamp not found in post.')
        t_now = datetime.utcnow()
        game_times_utc = np.array([t_now.replace(tzinfo=pytz.UTC)
                                   for i in range(n_games)])
    else:
        month = int(end_times[0].split('.')[1])
        year = (post_time.year + 1 if (post_time.month == 12) and (month == 1)
                else post_time.year)
        logging.debug('%d' % year)
        game_times = [datetime.strptime(str(year) + '.' + t, dt_format)
                      for t in end_times]
        game_times_utc = np.array([convert_timezone(t, from_tz='Europe/Athens',
                                                    to_tz='UTC')
                                   for t in game_times])
    return game_times_utc
