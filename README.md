underquotedbot
==============

[![Build Status](https://circleci.com/gh/jessamynsmith/underquotedbot.svg?style=shield)](https://circleci.com/gh/jessamynsmith/underquotedbot)
[![Coverage Status](https://coveralls.io/repos/jessamynsmith/underquotedbot/badge.svg?branch=master)](https://coveralls.io/r/jessamynsmith/underquotedbot?branch=master)

Twitter bot that replies to any mentions with a quotation, or posts a random quotation.
Please read Twitter's [Automation rules and best practices](https://support.twitter.com/articles/76915-automation-rules-and-best-practices/)
before setting up a bot.

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

In order to run unit tests, you must install and start redis, e.g. on OSX:

    brew install redis
    brew services start redis

Run tests with coverage (should be 100%) and check code style:

    coverage run -m nose
    coverage report -m
    flake8

Verify all supported Python versions:

    pip install tox
    tox

Run bot:

    PYTHONPATH=. ./bin/run_bot.py reply_to_mentions  # Check twitter stream for mentions, and reply
    PYTHONPATH=. ./bin/run_bot.py post_message       # Post a message to twitter

   
### Validating The Project Locally

The CircleCI build can be validated locally, using the CircleCI CLI and docker. 

First, install [Docker Desktop](https://www.docker.com/products/docker-desktop)

Then, install the CircleCI CLI, e.g. using homebrew on OSX:

    brew install circleci

Then, you can validate it by running this command in the terminal:

    circleci config validate

Once you know your config is valid, you can test it.
The CLI allows you to run a single job from CircleCI on your desktop using docker:

    circleci local execute --job build

For more information, see the [CircleCI docs](https://circleci.com/docs/2.0/local-cli/#validate-a-circleci-config)
 
    
Continuous Integration and Deployment
-------------------------------------

This project is already set up for continuous integration and deployment using circleci, coveralls,
and Heroku.

Make a new Heroku app, and add the following addons:

	Papertrail
	Redis To Go
	Heroku Scheduler

Enable the project on coveralls.io, and copy the repo token

Enable the project on circleci.io, and under Project Settings -> Environment variables, add:

    COVERALLS_REPO_TOKEN <value_copied_from_coveralls>
    
On circleci.io, under Project Settings -> Heroku Deployment, follow the steps to enable
Heroku builds. At this point, you may need to cancel any currently running builds, then run
a new build.

Once your app is deployed successfully, you can add the Scheduler tasks on Heroku:

    ./bin/run_bot.py reply_to_mentions
    ./bin/run_bot.py post_message
