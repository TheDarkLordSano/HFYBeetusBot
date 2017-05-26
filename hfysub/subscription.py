from celery import Celery
from beetusbot import config
import account
import requests.exceptions
import praw
import time
import math

app = Celery('subscriptions', broker=config.BROKER)
reddit = praw.Reddit(client_id=account.CLIENT_ID, client_secret=account.CLIENT_SECRET,
                     refresh_token=account.reftoken, user_agent='HFY Subscriptions contact /u/TheDarkLordSano',
                     username='TheDarkLordSano')


def filter_post(post):
    if post.link_flair_text is not None and any(k in post.link_flair_text.lower() for k in config.IGNORE):
        print "flair: %s" % post.link_flair_text
        return False
    else:
        return post.is_self and not any(k in post.title.lower() for k in config.IGNORE)


def mainSubscription():
    subreddit = reddit.subreddit(config.SUBREDDIT)

    latest = config.get_latest()

    for submission in subreddit.stream.submissions():
        check = filter_post(submission)
        if submission.id != latest and check:
            processSubmission(submission)


@app.task
def processSubmission(submission):
    if submission.author is None:  # wat? oh when a user deletes itself as author right away
        return

    createSubmissionReply(submission)


def get_stories_from(user):
    redditor = reddit.redditor(user)
    submitted = redditor.submissions.new(limit=20)
    filtered = [post for post in submitted if
                post.subreddit.display_name.lower() == config.SUBREDDIT.lower() and filter_post(post)]
    return filtered


@app.task
def createSubmissionReply(submission):
    all_stories = get_stories_from(submission.author.name)
    print "%s has %d stories" % (submission.author.name, len(all_stories))

    if len(all_stories) <= 0:
        print "User only has one story, not posting!"
        return
    for story in all_stories:
        previous_id = config.get_post_in_thread(story.id)
        post = construct_post(submission.author.name)
        posted = False
        while not posted:
            try:
                if previous_id:
                    #                    url=construct_url(story.id, previous_id)
                    #                    reddit.get_submission(url).comments[0].edit(post)
                    print "Not applicable %s" % previous_id
                else:
                    if story.id == submission.id:
                        subscriberservice.notify(submission, reddit)
                    subm = reddit.submission(id=story.id)
                    added = subm.reply(post)
                    config.add_post(story.id, story.author.name, added.id)
                    print "Added new comment: %s" % added.id
                posted = True
            except praw.exceptions.APIException, requests.exceptions.HTTPError:
                print "Too many requests, trying again in a minute."
                time.sleep(60)
            except praw.exceptions.APIException, err:
                if hasattr(err, "error_type") and err.error_type == 'TOO_OLD':
                    print "This post is too old, cannot reply."  # lets build something so it won't try to post again when a the user posts another story, shall we?
                    break
