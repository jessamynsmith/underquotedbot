underquotedbot
==============

[![Build Status](https://circleci.com/gh/jessamynsmith/underquotedbot.svg?style=shield)](https://circleci.com/gh/jessamynsmith/underquotedbot)
[![Coverage Status](https://coveralls.io/repos/jessamynsmith/underquotedbot/badge.svg?branch=master)](https://coveralls.io/r/jessamynsmith/underquotedbot?branch=master)

Replies to any twitter mentions with a quotation.

Settings are populated from environment variables. The authentication variables can be
[obtained from your Twitter account](https://dev.twitter.com/oauth/overview/application-owner-access-tokens/).

- TWITTER_CONSUMER_KEY
- TWITTER_CONSUMER_SECRET
- TWITTER_OAUTH_SECRET
- TWITTER_OAUTH_TOKEN
- QUOTATION_URL

for the underquoted, use the following QUOTATION_URL:
'https://underquoted.herokuapp.com/api/v2/quotations/?random=true&limit=1'

This project is set up to be deployed to heroku, using the Heroku Scheduler and RedisToGo addons.
There are two scheduled tasks set up:

    ./bin/run_bot.py post_message  # runs daily
    ./bin/run_bot.py reply_to_mentions  # runs every 10 minutes

Development
-----------

Fork the project on github and git clone your fork, e.g.:

    git clone https://github.com/<username>/underquotedbot.git

Set up virtualenv:

    mkvirtualenv underquotedbot
    pip install -r requirements/development.txt

Run tests:

    coverage run -m nose
    coverage report
    
Verify all supported Python versions:

    tox
    
Check code style:

    flake8

Run bot:

    ./bin/run_bot.py reply_to_mentions  # Check twitter stream for mentions, and reply
    ./bin/run_bot.py post_message       # Post a message to twitter
