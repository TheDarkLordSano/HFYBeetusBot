from __future__ import absolute_import, unicode_literals

from praw import Reddit

import account


def make_reddit():
    return Reddit(
        client_id=account.CLIENT_ID,
        client_secret=account.CLIENT_SECRET,
        refresh_token=account.reftoken,
        user_agent='HFY Subscriptions contact /u/TheDarkLordSano',
        username='TheDarkLordSano'
    )
