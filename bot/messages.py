import logging
import requests
import os

from twitter_bot import SettingsError


logging.basicConfig(filename='logs/bot.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    level=logging.DEBUG)


class QuotationProvider(object):

    def __init__(self, quotation_url=None):
        if not quotation_url:
            quotation_url = os.environ.get('QUOTATION_URL')
            if not quotation_url:
                raise SettingsError("You must supply quotation_url or set the QUOTATION_URL "
                                    "environment variable.")
        self.BASE_URL = quotation_url

    def create(self, mention):
        """
        Create a message
        :param mention: JSON object containing mention details from Twitter
        :return: a message
        """
        hashtags = [x['text'] for x in mention.get('entities', {}).get('hashtags', {})]

        message = 'No quotations found'
        if hashtags:
            hashed_tags = ['#%s' % x for x in hashtags]
            hash_message = " ".join(hashed_tags)
            message += ' matching {0}'.format(hash_message)

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
