from __future__ import absolute_import

from celery.utils.log import get_task_logger

from beetusbot import config
from .reddit_writer import send_message, write_post
from ..celery import app, RedditTask
from ..util import filter_post

logger = get_task_logger(__name__)


@app.task(base=RedditTask)
def process_submission(submission):
    submissions = process_submission.reddit.redditor(submission.author.name).submissions.new(limit=20)
    all_stories = [post for post in submissions if filter_post(post)]

    logger.info("%s has %d stories" % (submission.author.name, len(all_stories)))

    if len(all_stories) <= 0:
        logger.info("User only has one story, not posting!")
        return

    for story in all_stories:
        previous_id = config.get_post_in_thread(story.id)  #checks if the story is already in the 'repliedto' database.

        if not previous_id:   #If the story is not in the 'repliedto' database
            if story.id == submission.id:  #Is the place in the loop we are at the story that started this?
                queue_notifications(submission)   #Time to send people the notification.
				
            post = config.POST_CONTENT.format(username=submission.author.name)  
            write_post(story.id, post, submission.author.name)  #submit a reply on the story, write_post adds story to 'repliedto' database


@app.task
def queue_notifications(submission):
    subscribers = config.get_subscribers(submission.author)

    for subscriber in subscribers:
        if subscriber.lower() in config.stalkers:
            message = config.STALKER_NEW_CONTENT.format(
                username=subscriber,
                writer=submission.author,
                title=submission.title,
                url=submission.url.encode('utf8')
            )
        else:
            message = config.NEW_submission_CONTENT.format(
                username=subscriber,
                writer=submission.author,
                title=submission.title,
                url=submission.url.encode('utf8')
            )

        send_message(subscriber, "There's a new story for you!", message)
