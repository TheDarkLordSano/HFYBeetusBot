'''
Created on Oct 5, 2013

@author: Chris
'''
import praw
import config
import time
import requests.exceptions
import subscriberservice
reddit = praw.Reddit(user_agent='BeetusBot v0.001')
subreddit = reddit.get_subreddit(config.SUBREDDIT)
reddit.login(config.USERNAME, config.PASSWORD)
def main():
    subscriberservice.run(reddit)
    
    latest = config.get_latest()
    submissions = list(subreddit.get_new(limit=8, place_holder=latest))
    print "Got %d new submissions after %s" % (len(submissions) - 1, latest)
    if len(submissions) > 1:
        print "Saving latest"
        config.set_latest(submissions[0].id)
    else:
        print "No new submissions."
        
    for submission in submissions:
        if submission.id != latest and filter_post(submission):
            print "Handling %s" % submission.id 
            handle(submission)
        else:
            print "Submission is filtered out"
            
    print "Done, checking again in 5 minutes."
    

def handle(submission):  
    if submission.author is None: #wat? oh when a user deletes itself as author right away
        return
    all_stories = get_stories_from(submission.author.name)
    print "%s has %d stories" % (submission.author.name, len(all_stories))

    if len(all_stories) <= 1:
        print "User only has one story, not posting!"
        return
    for story in all_stories:
        previous_id = config.get_post_in_thread(story.id)
        post = construct_post(all_stories, story.id)
        posted = False
        while not posted:
            try:
                if previous_id:
                    url=construct_url(story.id, previous_id)
                    reddit.get_submission(url).comments[0].edit(post)
                    print "Edited previous comment %s" % previous_id
                else:
                    if story.id == submission.id:
                        subscriberservice.notify(submission, reddit)
                    subm = reddit.get_submission(submission_id=story.id)
                    added = subm.add_comment(post)
                    config.add_post(story.id, story.author.name, added.id)
                    print "Added new comment: %s" % added.id
                posted = True
            except praw.errors.RateLimitExceeded, requests.exceptions.HTTPError:
                print "Too many requests, trying again in a minute."
                time.sleep(60)
            except praw.errors.APIException, err:
                if hasattr(err, "error_type") and err.error_type == 'TOO_OLD':
                    print "This post is too old, cannot reply." #lets build something so it won't try to post again when a the user posts another story, shall we?
                    break

def construct_url(reddit_id, reply_id):
    return "http://www.reddit.com/r/%s/comments/%s/_/%s/" % (config.SUBREDDIT, reddit_id, reply_id)

def construct_post(submissions, current_id):
    posts = [("[%s%s](%s)" % (submission.title, " (this)" if submission.id == current_id else "", submission.url)) for submission in submissions]
    posts[0] = "* " + posts[0] #also add formatting to first item
    return config.POST_CONTENT.format(username = submissions[0].author.name, 
                                      text     = "\n\n* ".join(posts).encode('utf-8'))
    
def get_stories_from(user):
    redditor = reddit.get_redditor(user)
    submitted = redditor.get_submitted(limit=5000)
    filtered = [post for post in submitted if  post.subreddit.display_name == config.SUBREDDIT.lower() and filter_post(post)]
    filtered = sorted(filtered, key=lambda post: post.created, reverse=False)
    return filtered


def filter_post(post):
    if hasattr(post, "link_flair_text") and post.link_flair_text is not None and any(k in post.link_flair_text.lower() for k in config.IGNORE):
        return False
    return post.is_self and not any(k in post.title.lower() for k in config.IGNORE)
