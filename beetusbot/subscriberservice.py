'''
Created on 21 okt. 2013

@author: Chris

@Butcherer: TheDarkLordSano

@Nitpicker: Bontrose
'''
import sys
import config
import re
import praw
import time
import requests
user_regex = re.compile('\/([A-Za-z0-9_-]{1,})') #user regex

def get_new_messages(redd):
    return redd.inbox.unread(limit=None)

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

def do_reply(message, redd):
    print "Sending pm to %s about their subscriptions" % message.author
    pmed = False
    while not pmed:
        try:
            redd.redditor(unicode(message.author)).message("Subscription update",construct_pm(message.author, config.get_subscriptions(message.author)))
            pmed = True
        except praw.exceptions.APIException, requests.exceptions.HTTPError:
            print "503 error or something, sleeping for 60 seconds"
            time.sleep(60)
        except:
            print "Unknown error: ", sys.exc_info()[0], sys.exc_info()[1]
            time.sleep(60)
    message.mark_read()

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
		if(subscriber.lower() in config.stalkers):
		    messe = config.STALKER_NEW_CONTENT.format(username=subscriber,
                                                            writer=story.author,
                                                            title=story.title,
                                                            url=story.url.encode('utf8')
                                                            )
		else:
		    messe = config.NEW_STORY_CONTENT.format(username=subscriber,
                                                            writer=story.author,
                                                            title=story.title,
                                                            url=story.url.encode('utf8')
                                                            )
                reddit.redditor(subscriber).message("There's a new story for you!", messe)
                pmed = True
            except praw.exceptions.APIException, err:
                if hasattr(err, "error_type") and err.error_type == 'InvalidUser':
                    print "User %s doesn't exist anymore, removing from list!" % subscriber 
                    #catch incase user subscribes and then deletes the account.
                    config.remove_subscription(story.author, subscriber)
                    pmed = True
                elif hasattr(err, "error_type") and err.error_type == 'RATELIMIT':
                    print "503 error or something, sleeping for 60 seconds"
                    time.sleep(60)
            except:
                print "Unknown error: ", sys.exc_info()[0]
                time.sleep(60)
            

def run(redd):
    new_messages = get_new_messages(redd)
    for message in new_messages:

        if "unsubscribe" in message.body.lower() or "unsubscribe" in message.subject.lower():
            for user in extract_users(message.body):
                print "Removing subscription from %s to %s" % (user, message.author)
                config.remove_subscription(user, message.author)
                
            do_reply(message, redd)
        elif "subscribe" in message.body.lower() or "subscribe" in message.subject.lower():
            for user in extract_users(message.body):
#		print "Testing %s" % user
		if user.lower() == 'u':
                    continue
                else:
                    print "Added subscription from %s to %s" % (user, message.author)
                    config.add_subscription(user, message.author)
            do_reply(message, redd)

