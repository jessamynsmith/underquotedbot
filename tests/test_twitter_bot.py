import unittest
from mock import call, patch, MagicMock
from twitter.api import TwitterHTTPError

from twitter_bot.twitter_bot import main, Settings, TwitterBot


class TestSettings(unittest.TestCase):

    @patch('os.environ.get')
    def test_constructor_invalid(self, mock_env_get):
        mock_env_get.return_value = None

        try:
            Settings()
            self.fail('Should not be able to construct settings with None values')
        except ValueError:
            pass

    @patch('os.environ.get')
    def test_constructor_valid(self, mock_env_get):
        mock_env_get.return_value = 'bogus'

        settings = Settings()

        self.assertEqual(['bogus', 'bogus', 'bogus', 'bogus'], settings)


class TestTwitterBot(unittest.TestCase):

    MESSAGE = "You don't manage people, you manage things. You lead people. - Grace Hopper"
    LONG_MESSAGE = ("I have loved men and women in my life; I've been labeled 'the bisexual "
                    "defector' in print. Want to know another secret? I'm even ambidextrous. "
                    "I don't like labels. Just call me Martina. - Martina Navratilova")

    def setUp(self):
        self.settings = {'TWITTER_CONSUMER_KEY': 'bogus',
                         'TWITTER_CONSUMER_SECRET': 'bogus',
                         'TWITTER_OAUTH_SECRET': 'bogus',
                         'TWITTER_OAUTH_TOKEN': 'bogus'}
        self.bot = TwitterBot(self.settings,
                              redis_url='redis://:@localhost:6379/10',
                              quotation_url='http://invalid/quotation/?')

    @patch('os.environ.get')
    @patch('redis.Redis.from_url')
    def test_constructor_no_urls(self, mock_from_url, mock_env_get):
        mock_from_url.return_value = None
        mock_env_get.return_value = 'bogus'

        bot = TwitterBot(self.settings)

        self.assertEqual(None, bot.redis)
        self.assertEqual('bogus', bot.BASE_URL)

    def test_tokenize_short(self):
        messages = self.bot.tokenize(self.MESSAGE, 80)

        self.assertEqual(1, len(messages))
        self.assertEqual(self.MESSAGE, messages[0])

    def test_tokenize_too_long(self):
        messages = self.bot.tokenize(self.MESSAGE, 50)

        self.assertEqual(2, len(messages))
        for message in messages:
            self.assertTrue(len(message) <= 50)
        self.assertEqual("You don't manage people, you manage things. ...", messages[0])
        self.assertEqual("... You lead people. - Grace Hopper", messages[1])

    def test_tokenize_much_too_long(self):
        messages = self.bot.tokenize(self.MESSAGE, 30)

        self.assertEqual(4, len(messages))
        for message in messages:
            self.assertTrue(len(message) <= 30)
        self.assertEqual("You don't manage people, ...", messages[0])
        self.assertEqual("... you manage things. You ...", messages[1])
        self.assertEqual("... lead people. - Grace ...", messages[2])
        self.assertEqual("... Hopper", messages[3])

    def test_tokenize_short_with_mention(self):
        messages = self.bot.tokenize(self.MESSAGE, 80, '@js')

        self.assertEqual(1, len(messages))
        self.assertEqual('@js %s' % self.MESSAGE, messages[0])

    def test_tokenize_much_too_long_with_mention(self):
        messages = self.bot.tokenize(self.MESSAGE, 40, '@js')

        self.assertEqual(4, len(messages))
        for message in messages:
            self.assertTrue(len(message) <= 35)
        self.assertEqual("@js You don't manage people, ...", messages[0])
        self.assertEqual("@js ... you manage things. You ...", messages[1])
        self.assertEqual("@js ... lead people. - Grace ...", messages[2])
        self.assertEqual("@js ... Hopper", messages[3])

    def test_get_error_no_hashtags(self):
        error = self.bot.get_error('An error has occurred', [])

        self.assertEqual('An error has occurred', error)

    def test_get_error_with_hashtags(self):
        error = self.bot.get_error('An error has occurred', ['love', 'hate'])

        self.assertEqual('An error has occurred matching #love #hate', error)

    @patch('requests.get')
    def test_retrieve_quotation_success(self, mock_get):
        mock_result = MagicMock(status_code=200)
        mock_result.json.return_value = {'results': [{
            'text': 'Here I stay',
            'author': 'Henrietta'
        }]}
        mock_get.return_value = mock_result

        quotation = self.bot.retrieve_quotation([])

        self.assertEqual('Here I stay - Henrietta', quotation)
        mock_get.assert_called_with('http://invalid/quotation/?')

    @patch('requests.get')
    def test_retrieve_quotation_with_hashtags_success(self, mock_get):
        mock_result = MagicMock(status_code=200)
        mock_result.json.return_value = {'results': [{
            'text': 'Here I stay.',
            'author': 'Henrietta'
        }]}
        mock_get.return_value = mock_result

        quotation = self.bot.retrieve_quotation(['stay'])

        self.assertEqual('Here I stay. - Henrietta', quotation)
        mock_get.assert_called_with('http://invalid/quotation/?&search=stay')

    @patch('requests.get')
    def test_retrieve_quotation_no_quotations(self, mock_get):
        mock_result = MagicMock(status_code=200)
        mock_result.json.return_value = {'results': []}
        mock_get.return_value = mock_result

        quotation = self.bot.retrieve_quotation([])

        self.assertEqual('No quotations found', quotation)
        mock_get.assert_called_with('http://invalid/quotation/?')

    @patch('requests.get')
    def test_retrieve_quotation_error_no_hashtags(self, mock_get):
        mock_get.return_value = MagicMock(status_code=500)

        quotation = self.bot.retrieve_quotation([])

        self.assertEqual('No quotations found', quotation)
        mock_get.assert_called_with('http://invalid/quotation/?')

    @patch('requests.get')
    def test_retrieve_quotation_error_with_hashtags(self, mock_get):
        mock_get.return_value = MagicMock(status_code=500)

        quotation = self.bot.retrieve_quotation(['love', 'hate'])

        self.assertEqual('No quotations found matching #love #hate', quotation)
        mock_get.assert_called_with('http://invalid/quotation/?&search=love'
                                    '&search=hate')

    def test_post_quotation_short_no_mention(self):
        mock_statuses = MagicMock()
        self.bot.twitter.statuses = mock_statuses

        result = self.bot.post_quotation('Here I stay. - Henrietta')

        self.assertEqual(0, result)
        mock_statuses.update.assert_called_with(
            status='Here I stay. - Henrietta', in_reply_to_status_id=None)

    def test_post_quotation_too_long_with_mention(self):
        mock_statuses = MagicMock()
        self.bot.twitter.statuses = mock_statuses

        result = self.bot.post_quotation(self.LONG_MESSAGE,
                                         mentioner='@jessamyn', mention_id=2)

        self.assertEqual(0, result)
        expected_calls = [
            call(status="@jessamyn I have loved men and women in my life; I've been labeled "
                        "'the bisexual defector' in print. Want to know another ...",
                 in_reply_to_status_id=2),
            call(status="@jessamyn ... secret? I'm even ambidextrous. I don't like labels. "
                        "Just call me Martina. - Martina Navratilova", in_reply_to_status_id=2)]
        self.assertEqual(expected_calls, mock_statuses.update.mock_calls)

    def test_post_quotation_unknown_error(self):
        error = TwitterHTTPError(
            MagicMock(headers={'Content-Encoding': ''}), '', '', [])
        error.response_data = {"errors": [{"code": 187}]}
        mock_update = MagicMock(side_effect=error)
        mock_statuses = MagicMock()
        mock_statuses.update = mock_update
        self.bot.twitter.statuses = mock_statuses

        result = self.bot.post_quotation('Here I stay. - Henrietta')

        self.assertEqual(187, result)
        mock_statuses.update.assert_called_with(
            status='Here I stay. - Henrietta', in_reply_to_status_id=None)


class TestReplyToMentions(unittest.TestCase):

    def setUp(self):
        self.settings = {'TWITTER_CONSUMER_KEY': 'bogus',
                         'TWITTER_CONSUMER_SECRET': 'bogus',
                         'TWITTER_OAUTH_SECRET': 'bogus',
                         'TWITTER_OAUTH_TOKEN': 'bogus'}
        self.bot = TwitterBot(self.settings,
                              redis_url='redis://:@localhost:6379/10',
                              quotation_url='http://invalid/quotation/?')
        self.bot.twitter.statuses = MagicMock()
        self.bot.retrieve_quotation = MagicMock(return_value="'Tis better")
        self.bot.post_quotation = MagicMock()
        self.bot.redis = MagicMock(get=MagicMock(return_value=None))

    def test_reply_to_mentions_no_mentions_no_since_id(self):
        self.bot.twitter.statuses.mentions_timeline.return_value = []

        result = self.bot.reply_to_mentions()

        self.assertEqual(0, result)
        self.bot.twitter.statuses.mentions_timeline.assert_called_with(count=200)

    def test_reply_to_mentions_no_mentions_with_since_id(self):
        self.bot.twitter.statuses.mentions_timeline.return_value = []
        self.bot.redis.get.return_value = '3'

        result = self.bot.reply_to_mentions()

        self.assertEqual(0, result)
        self.bot.twitter.statuses.mentions_timeline.assert_called_with(
            count=200, since_id='3')
        self.bot.redis.get.assert_called_once_with('since_id')

    def test_reply_to_mentions_error(self):
        self.bot.twitter.statuses.mentions_timeline.return_value = [
            {'id': '123',
             'user': {'screen_name': 'jessamyn'},
             'entities': {'hashtags': [{'text': 'love'}]}}
        ]
        self.bot.post_quotation.return_value = 187

        result = self.bot.reply_to_mentions()

        self.assertEqual(1, result)
        self.bot.twitter.statuses.mentions_timeline.assert_called_once_with(count=200)
        self.assertEqual(11, len(self.bot.post_quotation.mock_calls))
        self.assertEqual(call("'Tis better", '@jessamyn', '123'),
                         self.bot.post_quotation.mock_calls[0])
        self.assertEqual(call('No quotations found matching #love', '@jessamyn', '123'),
                         self.bot.post_quotation.mock_calls[10])
        self.bot.redis.get.assert_called_once_with('since_id')
        self.bot.redis.set.assert_called_once_with('since_id', '123')

    def test_reply_to_mentions_success(self):
        self.bot.twitter.statuses.mentions_timeline.return_value = [
            {'id': '123',
             'user': {'screen_name': 'jessamyn'},
             'entities': {'hashtags': [{'text': 'love'}]}}
            ]
        self.bot.post_quotation.return_value = 0

        result = self.bot.reply_to_mentions()

        self.assertEqual(1, result)
        self.bot.twitter.statuses.mentions_timeline.assert_called_once_with(count=200)
        expected_calls = [call("'Tis better", '@jessamyn', '123')]
        self.assertEqual(expected_calls, self.bot.post_quotation.mock_calls)
        self.bot.redis.get.assert_called_once_with('since_id')
        self.bot.redis.set.assert_called_once_with('since_id', '123')

    def test_post_message(self):
        self.bot.post_quotation.return_value = 0

        result = self.bot.post_message()

        self.assertEqual(0, result)
        self.bot.post_quotation.assert_called_once_with("'Tis better")

    def test_main_no_args(self):
        result = main(self.settings, [])

        self.assertEqual(1, result)

    @patch('twitter_bot.twitter_bot.TwitterBot.post_message')
    @patch('redis.Redis.from_url')
    def test_main_invalid_arg(self, mock_from_url, mock_post):
        mock_from_url.return_value = None
        mock_post.return_value = 33

        result = main(self.settings, ['', 'bogus'])

        self.assertEqual(2, result)
        self.assertEqual(0, mock_post.call_count)

    @patch('twitter_bot.twitter_bot.TwitterBot.post_message')
    @patch('redis.Redis.from_url')
    def test_main_post_message(self, mock_from_url, mock_post):
        mock_from_url.return_value = None
        mock_post.return_value = 33

        result = main(self.settings, ['', 'post_message'])

        self.assertEqual(33, result)
        mock_post.assert_called_once_with()

    @patch('twitter_bot.twitter_bot.TwitterBot.reply_to_mentions')
    @patch('redis.Redis.from_url')
    def test_main_reply_to_mentions(self, mock_from_url, mock_reply):
        mock_from_url.return_value = None
        mock_reply.return_value = 0

        result = main(self.settings, ['', 'reply_to_mentions'])

        self.assertEqual(0, result)
        mock_reply.assert_called_once_with()
