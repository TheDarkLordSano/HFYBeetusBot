from __future__ import absolute_import, unicode_literals

from celery.utils.log import get_task_logger
import requests.exceptions
import praw
from ..models.subs import Subscriptions
from ..models.repto import repliedto
from beetusbot import config
from ..celery import app, RedditTask

logger = get_task_logger(__name__)


@app.task(bind=True, max_retries=3, rate_limit=config.WRITE_POST_RATE_LIMIT, base=RedditTask)
def write_post(self, parent_id, post, author_name):
    """

    :type self: RedditTask
    :type parent_id: str
    :type post: str
    :type author_name: str
    """
    try:
        submission = write_post.reddit.submission(id=parent_id)
        added = submission.reply(post)
		repliedto.objects.create(reddit_id=parent_id, author=author_name, replied_id=added.id)
    except (praw.exceptions.APIException, requests.exceptions.HTTPError) as exc:
        if hasattr(exc, "error_type") and exc.error_type == 'TOO_OLD':
            return
        raise self.retry(exc=exc)


@app.task(bind=True, max_retries=3, rate_limit=config.WRITE_PM_RATE_LIMIT, base=RedditTask)
def send_message(self, recipient, subject, message):
    """

    :type self: RedditTask
    :type recipient: str
    :type subject: str
    :type message: str
    """

    try:
        logger.info("sending message to %s" % recipient)
        send_message.reddit.redditor(recipient).message(subject, message)
    except praw.exceptions.APIException as exc:
        if hasattr(exc, "error_type") and exc.error_type == 'InvalidUser':
            logger.info("User %s doesn't exist anymore, removing from list!" % recipient)
            # catch in case user subscribes and then deletes the account.
            Subscriptions.objects.filter(subscriber=recipient).delete()
        elif hasattr(exc, "error_type") and exc.error_type == 'RATELIMIT':
            logger.warn("503 error or something, retrying")
            self.retry(exc=exc)

