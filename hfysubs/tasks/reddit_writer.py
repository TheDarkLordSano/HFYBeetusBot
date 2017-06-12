from __future__ import absolute_import, unicode_literals

from celery.utils.log import get_task_logger
import requests.exceptions
import praw

from beetusbot import config
from ..celery import app, RedditTask

logger = get_task_logger(__name__)


@app.task(bind=True, max_retries=3, rate_limit=config.WRITE_POST_RATE_LIMIT, base=RedditTask)
def write_post(self, parent_id, post, author_name):
    try:
        submission = write_post.reddit.submission(id=parent_id)
        added = submission.reply(post)
        config.add_post(parent_id, author_name, added.id)
    except (praw.exceptions.APIException, requests.exceptions.HTTPError) as exc:
        if hasattr(exc, "error_type") and exc.error_type == 'TOO_OLD':
            return
        raise self.retry(exc=exc)


@app.task(bind=True, max_retries=3, rate_limit=config.WRITE_PM_RATE_LIMIT, base=RedditTask)
def send_message(self, recipient, subject, message):
    #print "Attempting to send message to: ", recipient
    try:
        logger.info("sending message to %s" % recipient)
        send_message.reddit.redditor(recipient).message(subject, message)
    except praw.exceptions.APIException as exc:
        if hasattr(exc, "error_type") and exc.error_type == 'InvalidUser':
            logger.info("User %s doesn't exist anymore, removing from list!" % recipient)
            # catch incase user subscribes and then deletes the account.
            config.clear_subscriptions(recipient)
        elif hasattr(exc, "error_type") and exc.error_type == 'RATELIMIT':
            logger.warn("503 error or something, retrying")
            self.retry(exc=exc)

