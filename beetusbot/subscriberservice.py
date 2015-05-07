'''
Created on 21 okt. 2013

@author: Chris
'''
import sys
import config
import re
import praw
import time
import requests
user_regex = re.compile('\/u\/([A-Za-z0-9_-]{1,})') #user regex

class MockStory(): #I guess I should remove this
    def __init__(self, author, title, url):
        self.author = author
        self.title = title
        self.url = url

def get_new_messages(redd):
    return redd.get_unread(limit=None)

def extract_users(message):
    return user_regex.findall(message)

def construct_pm(author, subscriptions):
    subscriptions = [subscription[0] for subscription in subscriptions]
    if len(subscriptions) >= 1:
        subscriptions[0] = "* " + subscriptions[0]
        userlist = "\n\n* ".join(subscriptions)
        return config.SUBSCRIPTION_CONTENT.format(username=author,
                                                  text=userlist)
    else:
        return config.SUBSCRIPTION_CONTENT.format(username=author,
                                                  text="You don't have any subscriptions")

def do_reply(message):
    print "Sending pm to %s about their subscriptions" % message.author
    message.reply(construct_pm(message.author, config.get_subscriptions(message.author)))
    message.mark_as_read()

def reply_list(message, users):
    print "Sending pm to %s because (s)he requested a list from %s" % (message.author, users) 

def send_message(sub, title, body):
    print "Send message %s to %s, content: \r\n%s" % (title, sub, body)

def notify(story, reddit):
    config.add_notification_request(story.id)
    print "Added req id %s to DB" % story.id

def send_notifications(story, reddit):
    subs = config.get_subscribers(story.author)
    for sub in subs:
        subscriber = sub[0]
        pmed = False
        print "Sending message to %s about a new story from %s" % (subscriber, story.author)
        while not pmed:
            try:
                message = config.NEW_STORY_CONTENT.format(username=subscriber,
                                                            writer=story.author,
                                                            title=story.title,
                                                            url=story.url.encode('utf8')
                                                            )
                reddit.send_message(subscriber, "There's a new story for you!", message)
                pmed = True
            except praw.errors.InvalidUser: #catch incase user subscribes and then deletes the account.
                print "User %s doesn't exist anymore, removing from list!" % subscriber
                config.remove_subscription(story.author, subscriber)
                pmed = True
            except praw.errors.RateLimitExceeded, requests.exceptions.HTTPError:
                print "503 error or something, sleeping for 60 seconds"
                time.sleep(60)
            except:
                print "Unknown error: ", sys.exc_info()[0]
                time.sleep(60)
            

def run(redd):
    new_messages = get_new_messages(redd)
    for message in new_messages:
        if hasattr(message, 'context') and message.context is not None and len(message.context) > 2:
            continue #is a comment reply, ignore
        if "unsubscribe" in message.body.lower() or "unsubscribe" in message.subject.lower():
            for user in extract_users(message.body):
                print "Removing subscription from %s to %s" % (user, message.author)
                config.remove_subscription(user, message.author)
                
            do_reply(message)
        elif "subscribe" in message.body.lower() or "subscribe" in message.subject.lower():
            for user in extract_users(message.body):
                print "Added subscription from %s to %s" % (user, message.author)
                config.add_subscription(user, message.author)
            do_reply(message)
