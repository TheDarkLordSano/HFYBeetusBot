from __future__ import absolute_import, unicode_literals

import sys, os, django
sys.path.append("/home/pi/HFYDB")
os.environ["DJANGO_SETTINGS_MODULE"] = "HFYDB.settings"
django.setup()

from .reddit import make_reddit
from beetusbot import config
from .tasks import process_submission, SerializableSubmission
from .util import filter_post
from prawcore.exceptions import PrawcoreException
from .models.repto import repliedto

import praw.exceptions

def handle_subscription_stream():
    subreddit = make_reddit().subreddit(config.SUBREDDIT)

    for submission in subreddit.stream.submissions():
	try:
            # checks if the story/submission is already in the 'repliedto' database.
            previous_id = repliedto.objects.filter(reddit_id=submission.id).exists()
            # author may be None when a user deletes itself as author right away
            if (not previous_id) and filter_post(submission) and submission.author is not None:
                # Convert the submission into something we can be sure will get serialized properly
                serializable_sub = SerializableSubmission(
                    submission.id,
                    submission.author.name,
                    submission.title.encode('utf-8'),
                    submission.url
                )

                process_submission(serializable_sub)
	except PrawcoreException as e:
            logging.exception('Exception %S', e, exc_info=True)
            time.sleep(30)
