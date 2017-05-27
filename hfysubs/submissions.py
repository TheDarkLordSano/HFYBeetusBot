from __future__ import absolute_import, unicode_literals

from .reddit import make_reddit
from beetusbot import config
from .tasks import process_submission
from .util import filter_post


def handle_subscription_stream():
    subreddit = make_reddit().subreddit(config.SUBREDDIT)

    latest = config.get_latest()

    for submission in subreddit.stream.submissions():
        check = filter_post(submission)
        if submission.id != latest and check and submission.author is not None:
            if submission.author is None:  # wat? oh when a user deletes itself as author right away
                process_submission(submission)
