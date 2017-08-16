from __future__ import absolute_import
from collections import namedtuple

import sys, os, django
sys.path.append("/home/pi/HFYDB")
os.environ["DJANGO_SETTINGS_MODULE"] = "HFYDB.settings"
django.setup()

from celery.utils.log import get_task_logger

from beetusbot import config
from .reddit_writer import send_message, write_post
from ..celery import app, RedditTask
from ..util import filter_post
from ..models.repto import repliedto
from ..models.subs import Subscriptions

logger = get_task_logger(__name__)


SerializableSubmission = namedtuple("SerializableSubmission", ["submissionId", "author", "title", "url"])


@app.task(base=RedditTask)
def process_submission(_submission):
    # Ensure we are working with a correctly deserialized SerializableSubmission
    # a named tuple gets serialized in JSON as an array, which means we can reconstruct our
    # named tuple by exploding it into the named tuples constructor
    # If this method is called directly, then the named tuple will be exploded into the constructor
    # which while not idea, will also not cause an issue
    """

    :type _submission: SerializableSubmission | (str, str, str, str)
    """
    submission = SerializableSubmission(*_submission)

    submissions = process_submission.reddit.redditor(submission.author).submissions.new(limit=20)
    all_stories = [post for post in submissions if filter_post(post)]

    logger.info("%s has %d stories" % (submission.author, len(all_stories)))

    if len(all_stories) <= 0:
        logger.info("User only has No stories? Weird.")
        return

    qlist = list(repliedto.objects.filter(author=submission.author).values_list("reddit_id", flat=True))

    for story in all_stories:
        # If the story is not in the 'repliedto' database
        if story.id.encode('UTF8') not in qlist:
            # Is the place in the loop we are at the story that started this?
            if story.id == submission.submissionId:
                # Time to send people the notification.
                queue_notifications(submission)

            post = config.POST_CONTENT.format(username=submission.author.replace("_", "\_").replace("-", "\-"))
            # submit a reply on the story, write_post adds story to 'repliedto' database
            # write_post Should not be .delay in this instance. By not sending it to celery queue the main process,
            # which searches for new stories, pauses to post on the submission while the messages of a new post are being sent out
            # this should prevent the script from placing the same story 3+ times in the queue waiting for it to be processed.
            write_post(story.id, post, submission.author)


@app.task
def queue_notifications(_submission):
    """

    :type _submission: SerializableSubmission | (str, str, str, str)
    """
    submission = SerializableSubmission(*_submission)

    subscribers = list(Subscriptions.objects.filter(subscribed_to__iexact=submission.author).values_list("subscriber", flat=True))

    for subscriber in subscribers:
        message = config.NEW_STORY_CONTENT.format(
            username=subscriber,
            writer=submission.author.replace("_", "\_").replace("-", "\-"),
            title=submission.title,
            url=submission.url
        )
        send_message.delay(subscriber, "There's a new story for you!", message)
