import unittest

from mock import patch

from bot.messages import QuotationProvider
from bot.settings import UnderquotedBotSettings


class TestSettings(unittest.TestCase):

    @patch('os.environ.get')
    def test_constructor_valid(self, mock_env_get):
        mock_env_get.return_value = 'bogus'

        settings = UnderquotedBotSettings()

        self.assertEqual('bogus', settings.OAUTH_TOKEN)
        self.assertEqual(QuotationProvider, settings.MESSAGE_PROVIDER)
