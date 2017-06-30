from __future__ import absolute_import
from collections import namedtuple

from celery.utils.log import get_task_logger

from beetusbot import config
from .reddit_writer import send_message, write_post
from ..celery import app, RedditTask
from ..util import filter_post

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
        logger.info("User only has one story, not posting!")
        return

    for story in all_stories:
        # checks if the story is already in the 'repliedto' database.
        previous_id = config.get_post_in_thread(story.id)

        # If the story is not in the 'repliedto' database
        if not previous_id:
            # Is the place in the loop we are at the story that started this?
            if story.id == submission.submissionId:
                # Time to send people the notification.
                queue_notifications(submission)

            post = config.POST_CONTENT.format(username=submission.author.name)
            # submit a reply on the story, write_post adds story to 'repliedto' database
            write_post.delay(story.id, post, submission.author.name)


@app.task
def queue_notifications(_submission):
    """

    :type _submission: SerializableSubmission | (str, str, str, str)
    """
    submission = SerializableSubmission(*_submission)

    subscribers = config.get_subscribers(submission.author)

    for subscriber in subscribers:
        # this is to get rid of the tuple
        subber = subscriber[0]
        message = config.NEW_STORY_CONTENT.format(
            username=subber,
            writer=submission.author,
            title=submission.title,
            url=submission.url
        )
        send_message.delay(subber, "There's a new story for you!", message)
