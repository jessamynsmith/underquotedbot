import logging
import os
import sys

import redis
import requests
from twitter import Twitter
from twitter.oauth import OAuth
from twitter.api import TwitterHTTPError

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                    level=logging.INFO)


class Settings(list):

    def __init__(self):
        super(Settings, self).__init__()
        tokens = ('OAUTH_TOKEN', 'OAUTH_SECRET', 'CONSUMER_KEY', 'CONSUMER_SECRET')
        for token in tokens:
            key = 'TWITTER_%s' % token
            value = os.environ.get(key)
            if not value:
                raise ValueError("Must set environment variable '%s'" % key)
            self.append(value)


def get_redis(redis_url=None):
    if not redis_url:
        redis_url = os.getenv('REDISTOGO_URL')
    return redis.Redis.from_url(redis_url)


class TwitterBot(object):

    def __init__(self, settings, redis_url=None, quotation_url=None):
        self.DUPLICATE_CODE = 187

        if not quotation_url:
            quotation_url = os.environ.get('QUOTATION_URL')
        self.BASE_URL = quotation_url

        self.twitter = Twitter(auth=OAuth(*settings))
        self.redis = get_redis(redis_url)

    def tokenize(self, message, message_length, mentioner=None):
        if mentioner:
            message = '%s %s' % (mentioner, message)
        if len(message) < message_length:
            return [message]

        # -4 for trailing ' ...'
        max_length = message_length - 4
        mentioner_length = 0
        if mentioner:
            # adjust for initial "@mentioner " on each message
            mentioner_length = len(mentioner) + 1
            max_length -= mentioner_length
        tokens = message.split(' ')
        indices = []
        index = 1
        length = len(tokens[0])
        for i in range(1, len(tokens)):
            if length + 1 + len(tokens[i]) >= max_length:
                indices.append(index)
                # 3 for leading "..."
                length = 3 + mentioner_length + len(tokens[i])
            else:
                length += 1 + len(tokens[i])
            index += 1

        indices.append(index)

        messages = [" ".join(tokens[0:indices[0]])]
        for i in range(1, len(indices)):
            messages[i-1] += ' ...'
            parts = []
            if mentioner:
                parts.append(mentioner)
            parts.append("...")
            parts.extend(tokens[indices[i-1]:indices[i]])
            messages.append(" ".join(parts))

        return messages

    def get_error(self, base_message, hashtags):
        message = base_message
        if len(hashtags) > 0:
            hashed_tags = ['#%s' % x for x in hashtags]
            hash_message = " ".join(hashed_tags)
            message = '%s matching %s' % (base_message, hash_message)
        return message

    def retrieve_quotation(self, hashtags=[]):
        message = self.get_error('No quotations found', hashtags)

        url = self.BASE_URL
        for hashtag in hashtags:
            url = '%s&search=%s' % (url, hashtag)
        logging.debug("Trying URL: %s" % url)
        result = requests.get(url)
        logging.debug("Quotation request, status code=%s" % result.status_code)

        if result.status_code == 200:
            quotations = result.json()
            if len(quotations['results']) > 0:
                quotation = quotations['results'][0]
                message = '%s - %s' % (quotation['text'], quotation['author'])

        return message

    def post_quotation(self, quotation, mentioner=None, mention_id=None):
        messages = self.tokenize(quotation, 140, mentioner)
        code = 0
        for message in messages:
            try:
                self.twitter.statuses.update(status=message,
                                             in_reply_to_status_id=mention_id)
            except TwitterHTTPError as e:
                logging.error('Unable to post to twitter: %s' % e)
                code = e.response_data['errors'][0]['code']
        return code

    def reply_to_mentions(self):
        since_id = self.redis.get('since_id')
        logging.debug("Retrieved since_id: %s" % since_id)

        kwargs = {'count': 200}
        if since_id:
            kwargs['since_id'] = since_id.strip()

        mentions = self.twitter.statuses.mentions_timeline(**kwargs)
        logging.info("Retrieved %s mentions" % len(mentions))

        mentions_processed = 0
        # We want to process least recent to most recent, so that since_id is set properly
        for mention in reversed(mentions):
            mention_id = mention['id']
            mentioner = '@%s' % mention['user']['screen_name']

            hashtags = []
            for hashtag in mention['entities']['hashtags']:
                hashtags.append(hashtag['text'])

            error_code = self.DUPLICATE_CODE
            tries = 0
            quotation = ''
            while error_code == self.DUPLICATE_CODE:
                if tries > 10:
                    logging.error('Unable to post duplicate message to %s: %s'
                                  % (mentioner, quotation))
                    break
                elif tries == 10:
                    quotation = self.get_error('No quotations found', hashtags)
                else:
                    quotation = self.retrieve_quotation(hashtags)
                error_code = self.post_quotation(quotation, mentioner,
                                                 mention_id)
                tries += 1

            mentions_processed += 1
            logging.info("Attempting to store since_id: %s" % mention_id)
            self.redis.set('since_id', mention_id)

        return mentions_processed

    def post_message(self):
        quotation = self.retrieve_quotation()
        return self.post_quotation(quotation)


def main(settings, args):
    error = "You must specify a single command, either 'post_message' or 'reply_to_mentions'"

    if len(args) != 2:
        print(error)
        return 1

    command = args[1]
    bot = TwitterBot(settings)

    result = 0
    if command == 'post_message':
        result = bot.post_message()
    elif command == 'reply_to_mentions':
        result = bot.reply_to_mentions()
    else:
        print(error)
        result = 2

    return result


if __name__ == '__main__':
    res = main(Settings(), sys.argv)
    if res != 0:
        sys.exit(res)
