'''
Created on Oct 5, 2013
SHOULD PROBABLY CHANGE THIS TO SOME NICE ORM AND STUFF
PLS FIX

@author: Chris
'''
import MySQLdb

SUBREDDIT = "FatPeopleStories"
POST_CONTENT = """
Other stories from /u/{username}:

{text}

_____
^If ^you ^want ^to ^get ^notified ^as ^soon ^as ^{username} ^posts ^a ^new ^story, [^click ^here](http://www.reddit.com/message/compose/?to=BeetusBot&subject=subscribe&message=subscribe%20/u/{username})^.

^(Hi I'm BeetusBot, for more info about me go to /r/beetusbot)
"""# pls replace the ^'s with one ^() and test it

SUBSCRIPTION_CONTENT = """
Hello there {username}! You are now subscribed to the following users:

{text}

_____
^(To unsubscribe to any of these users, send a message that contains the word unsubscribe and a list of users, for example: unsubscribe /u/username /u/username2)
"""

NEW_STORY_CONTENT = """
Hello {username}!

/u/{writer} just posted a new story called "{title}".

[Click here to read it]({url})

_____
^(To unsubscribe, send a message that contains the word unsubscribe and a list of users, for example: unsubscribe /u/username /u/username2)
"""

IGNORE = ["f2f", "fat2fit", "meta", "titp", "[tp]"]
FOOTER_TEXT = "Hi im BeetusBot" #not used?
USERNAME = "BeetusBot"
PASSWORD = ""

DATABASE_HOST = ""
DATABASE_USER = ""
DATABASE_PASS = ""
DATABASE_DB = ""

def connect(): #connecting for every query? wow..
    db_connection = MySQLdb.connect(DATABASE_HOST, DATABASE_USER, DATABASE_PASS, DATABASE_DB)
    return db_connection

def get_latest():
    with open("latest.txt") as f:
        return f.readline() #closing is overrated

def set_latest(reddit_id):
    with open("latest.txt", "w") as f:
        f.write(reddit_id)

def get_post_in_thread(id):
    db_connection = connect()
    cursor = db_connection.cursor()
    cursor.execute("SELECT replied_id FROM repliedto  WHERE reddit_id='%s'" % id)
    id = cursor.fetchone()
    db_connection.close()
    return False if id is None else id[0]

def add_notification_request(reddit_id):
    db_connection = connect()
    cursor = db_connection.cursor()
    cursor.execute('INSERT INTO notifications(reddit_id, done) VALUES("%s", "%d")' % (reddit_id, 0))
    db_connection.commit()
    db_connection.close()
    
def get_new_stories():
    db_connection = connect()
    cursor = db_connection.cursor()
    cursor.execute("SELECT reddit_id FROM notifications WHERE done=0")
    items = cursor.fetchall()
    db_connection.close()
    return [item[0] for item in items]

def mark_checked(id):
    db_connection = connect()
    cursor = db_connection.cursor()
    cursor.execute("UPDATE notifications SET done=1 WHERE reddit_id='%s'" % id)
    db_connection.commit()
    db_connection.close
    return

def add_post(parent, user, reply_id):
    db_connection = connect()
    cursor = db_connection.cursor()
    try:
        cursor.execute('INSERT INTO repliedto(reddit_id, user, replied_id) VALUES("%s", "%s", "%s")' % (parent, user, reply_id))
        db_connection.commit()
    except:
        print "Something went wrong when adding to the database!"
        db_connection.rollback()
    db_connection.close()
   
def get_subscriptions(subscriber):
    db_connection = connect()
    cursor = db_connection.cursor()
    cursor.execute('SELECT subscribed_to FROM subscriptions WHERE subscriber="%s"' % subscriber)
    items = cursor.fetchall()
    db_connection.close()
    return items
   
def get_subscribers(writer):
    db_connection = connect()
    cursor = db_connection.cursor()
    cursor.execute('SELECT subscriber FROM subscriptions WHERE subscribed_to="%s"' % writer)
    items = cursor.fetchall()
    db_connection.close()
    return items
    
def remove_subscription(writer, subscriber):
    db_connection = connect()
    cursor = db_connection.cursor()
    try:
        cursor.execute('DELETE FROM subscriptions WHERE subscribed_to="%s" AND subscriber="%s" AND subreddit="fatpeoplestories"' % (writer, subscriber))
        db_connection.commit()
    except:
        print "Something went wrong when removing subscription to the database. Subscription possibly doesn't exists."
        db_connection.rollback()
    db_connection.close()
    
def add_subscription(writer, subscriber):
    db_connection = connect()
    cursor = db_connection.cursor()
    try:
        cursor.execute('INSERT INTO subscriptions(subscribed_to, subscriber, subreddit) VALUES("%s", "%s", "FatPeopleStories")' % (writer, subscriber))
        db_connection.commit()
    except:
        print "Something went wrong when adding subscription to the database. Subscription possibly already exists."
        db_connection.rollback()
    db_connection.close()
