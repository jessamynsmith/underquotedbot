underquotedbot
==============

[![Build Status](https://travis-ci.org/jessamynsmith/underquotedbot.svg?branch=master)](https://travis-ci.org/jessamynsmith/underquotedbot)
[![Coverage Status](https://coveralls.io/repos/jessamynsmith/twitterbot/badge.svg?branch=master)](https://coveralls.io/r/jessamynsmith/twitterbot?branch=master)

Replies to any twitter mentions with a quotation.
This project is already set up to be deployed to heroku. You will need a redis addon, and probably
a scheduler to run the scripts in bin.

Note: Must set up 5 environment variables:
- TWITTER_CONSUMER_KEY
- TWITTER_CONSUMER_SECRET
- TWITTER_OAUTH_SECRET
- TWITTER_OAUTH_TOKEN
- QUOTATION_URL

for the underquoted, use the following QUOTATION_URL:
'https://underquoted.herokuapp.com/api/v2/quotations/?random=true&limit=1'

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

    sh bin/run_bot.sh reply_to_mentions  # Check twitter stream for mentions, and reply
    sh bin/run_bot.sh post_message       # Post a message to twitter
