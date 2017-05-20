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
        print "Notifying about %s" % id
 #       url = "https://www.reddit.com/r/%s/comments/%s/_/" % (config.SUBREDDIT, id)
        config.mark_checked(id)
        submission = bot.reddit.submission(id=id)
        subscriberservice.send_notifications(submission, bot.reddit)      