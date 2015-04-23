#!/usr/bin/env python

import logging
import sys

from twitter_bot import BotRunner

from bot.settings import UnderquotedBotSettings


logging.basicConfig(filename='logs/bot.log',
                    filemode='a',
                    format='%(asctime)s %(name)s %(levelname)s %(message)s',
                    level=logging.DEBUG)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("You must specify a single command, either 'post_message' or 'reply_to_mentions'")
        result = 1
    else:
        result = BotRunner().go(UnderquotedBotSettings(), sys.argv[1])
    sys.exit(result)
