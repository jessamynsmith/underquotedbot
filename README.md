underquotedbot
==============

[![Build Status](https://travis-ci.org/jessamynsmith/underquotedbot.svg?branch=master)](https://travis-ci.org/jessamynsmith/underquotedbot)
[![Coverage Status](https://coveralls.io/repos/jessamynsmith/twitterbot/badge.svg?branch=master)](https://coveralls.io/r/jessamynsmith/twitterbot?branch=master)

Replies to any twitter mentions with a quotation. This project is already set up to be deployed to heroku.

Note: Must set up 5 environment variables:
- TWITTER_CONSUMER_KEY
- TWITTER_CONSUMER_SECRET
- TWITTER_OAUTH_SECRET
- TWITTER_OAUTH_TOKEN
- QUOTATION_URL

for the underquoted, use the following QUOTATION_URL:
'https://underquoted.herokuapp.com/api/v1/quotations/?format=json&random=true&limit=1'

Development
-----------

Get source:

    git clone https://github.com/jessamynsmith/underquotedbot

Set up virtualenv:

    mkvirtualenv underquotedbot --python=/path/to/python3
    pip install -r requirements/development.txt

Run tests:

    coverage run -m nose
    coverage report

Run bot:

    python bin/reply_to_mentions.py  # Check twitter stream for mentions, and reply
    python bin/post_message.py       # Post a message to twitter
