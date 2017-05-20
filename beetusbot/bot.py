'''
Created on Oct 5, 2013

@author: Chris

@Butcherer TheDarkLordSano
'''
import praw
import config
import time
import math
import account
import requests.exceptions
import subscriberservice
#import OAuth2Util
#import pickle

reddit = praw.Reddit(client_id=account.CLIENT_ID, client_secret=account.CLIENT_SECRET, refresh_token=account.reftoken, user_agent='HFY Subscriptions contact /u/TheDarkLordSano', username='TheDarkLordSano')
subreddit = reddit.subreddit(config.SUBREDDIT)

#reddit.set_oauth_app_info(account.CLIENT_ID, account.CLIENT_SECRET, account.REDIRECT_URI)
#o = OAuth2Util.OAuth2Util(reddit, configfile="Authent.ini")
#o.refresh()

   

def main():
    subscriberservice.run(reddit)
   
    latest = config.get_latest()

    now = math.floor(time.time()-720)

    submissions = list(subreddit.submissions(start=now))
    print "Got new submissions after %s" % latest
    if len(submissions) > 1:
        print "Saving latest"
        config.set_latest(submissions[0].id)
    else:
        print "No new submissions."
        
    for submission in submissions:
#     for submission in subreddit.stream.submissions():
        check = filter_post(submission)
        if submission.id != latest and check:
            print "Handling %s" % submission.id 
            handle(submission)
        else:
            print "Submission is filtered out"
            if check:
                print submission.link_flair_text
            
    print "Done, checking again in 10 minutes."
    

def handle(submission):  
    if submission.author is None: #wat? oh when a user deletes itself as author right away
        return
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
                    print "This post is too old, cannot reply." #lets build something so it won't try to post again when a the user posts another story, shall we?
                    break

def construct_url(reddit_id, reply_id):
    return "http://www.reddit.com/r/%s/comments/%s/_/%s/" % (config.SUBREDDIT, reddit_id, reply_id)

def construct_post(author):
    return config.POST_CONTENT.format(username = author)
    
def get_stories_from(user):
    redditor = reddit.redditor(user)
    submitted = redditor.submissions.new(limit=20)
    filtered = [post for post in submitted if post.subreddit.display_name.lower() == config.SUBREDDIT.lower() and filter_post(post)]
    return filtered


def filter_post(post):
    if post.link_flair_text is not None and any(k in post.link_flair_text.lower() for k in config.IGNORE):
        print "flair: %s" % post.link_flair_text
        return False
    else:
        return post.is_self and not any(k in post.title.lower() for k in config.IGNORE)
