from __future__ import absolute_import, unicode_literals

from .reddit import make_reddit
from beetusbot import config
from .tasks import process_submission
from .util import filter_post


def handle_subscription_stream():
    subreddit = make_reddit().subreddit(config.SUBREDDIT)

    for submission in subreddit.stream.submissions():
        # author may be None when a user deletes itself as author right away
        if filter_post(submission) and submission.author is not None:
            process_submission(submission)
