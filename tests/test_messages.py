import unittest

from mock import MagicMock, patch
from twitter_bot import SettingsError

from bot.messages import QuotationProvider


class TestQuotationProvider(unittest.TestCase):

    def setUp(self):
        self.provider = QuotationProvider(quotation_url='http://localhost/?')

    @patch('os.environ.get')
    def test_constructor_empty_mongo_env_var(self, mock_env_get):
        mock_env_get.return_value = ''

        try:
            QuotationProvider()
            self.fail("Should not be able to instantiate provider without mongo")
        except SettingsError as e:
            error = "You must supply quotation_url or set the QUOTATION_URL environment variable."
            self.assertEqual(error, '{0}'.format(e))

    @patch('requests.get')
    def test_create_error_no_hashtags(self, mock_get):
        mock_get.return_value = MagicMock(status_code=500)

        quotation = self.provider.create({}, 140)

        self.assertEqual('No quotations found', quotation)
        mock_get.assert_called_with('http://localhost/?')

    @patch('requests.get')
    def test_create_error_with_hashtags(self, mock_get):
        mock_get.return_value = MagicMock(status_code=500)
        mention = {'entities': {'hashtags': [{'text': 'love'}, {'text': 'hate'}]}}

        quotation = self.provider.create(mention, 140)

        self.assertEqual('No quotations found matching #love #hate', quotation)
        mock_get.assert_called_with('http://localhost/?&search=love'
                                    '&search=hate')

    @patch('requests.get')
    def test_create_no_quotations(self, mock_get):
        mock_result = MagicMock(status_code=200)
        mock_result.json.return_value = {'results': []}
        mock_get.return_value = mock_result

        quotation = self.provider.create({}, 140)

        self.assertEqual('No quotations found', quotation)
        mock_get.assert_called_with('http://localhost/?')

    @patch('requests.get')
    def test_create_success(self, mock_get):
        mock_result = MagicMock(status_code=200)
        mock_result.json.return_value = {'results': [{
            'text': 'Here I stay',
            'author': 'Henrietta'
        }]}
        mock_get.return_value = mock_result

        message = self.provider.create({}, 140)

        self.assertEqual('Here I stay - Henrietta', message)
