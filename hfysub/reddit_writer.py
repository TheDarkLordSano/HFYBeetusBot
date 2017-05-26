from celery import Celery
from beetusbot import config
import account
import requests.exceptions
import praw

app = Celery('redditwriter', broker=config.BROKER)
reddit = praw.Reddit(client_id=account.CLIENT_ID, client_secret=account.CLIENT_SECRET,
                     refresh_token=account.reftoken, user_agent='HFY Subscriptions contact /u/TheDarkLordSano',
                     username='TheDarkLordSano')


@app.task(bind=True, max_retries=3, rate_limit=config.WRITE_POST_RATE_LIMIT)
def writePost(self, parent_id, post, author_name):
    try:
        submission = reddit.submission(id=parent_id)
        added = submission.reply(post)
        config.add_post(parent_id, author_name, added.id)
    except (praw.exceptions.APIException, requests.exceptions.HTTPError) as exc:
        if hasattr(exc, "error_type") and exc.error_type == 'TOO_OLD':
            return
        raise self.retry(exc=exc)
