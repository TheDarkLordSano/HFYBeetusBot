from beetusbot import config
from beetusbot import bot
from beetusbot import subscriberservice
import sys

if __name__ == "__main__":
    stories = config.get_new_stories()
    
    if len(stories) == 0:
        print "No notifications to send"
        sys.exit()
    
    for id in stories:
        config.mark_checked(id)

    for id in stories:
        print "Notifying about %s" % id
        url = "http://www.reddit.com/r/%s/comments/%s/_/" % (config.SUBREDDIT, id)
        submission = bot.reddit.get_submission(url)
        subscriberservice.send_notifications(submission, bot.reddit)
        