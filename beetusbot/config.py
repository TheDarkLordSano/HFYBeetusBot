'''
Created on Oct 5, 2013
@author: Chris
Edited 4/24/2015 
@additions: TheDarkLordSano
'''
import sqlite3

SUBREDDIT = "HFY"
POST_CONTENT = """
Like this story and want to be notified when a story is posted?

Reply with: Subscribe: /{username}

Already tired of the author?

Reply with: Unsubscribe: /{username}
_____
Don't want to admit your like or dislike to the community? [click here](http://www.reddit.com/message/compose/?to=HFYsubs&subject=subscribe&message=subscribe%20/u/{username}) and send the same message.
_____
If I'm broke Contact user 'TheDarkLordSano' via PM or IRC.  
____
[I have a wiki page](https://www.reddit.com/r/HFY/wiki/tools/hfysubs)
____

UPGRADES IN PROGRESS. REQUIRES MORE VESPENE GAS.
"""

SUBSCRIPTION_CONTENT = """
Hello there {username}! You are now subscribed to the following users:

{text}

_____
^(To unsubscribe to any of these users, send a message that contains the word unsubscribe and a list of users, for example: unsubscribe /u/username /u/username2)
_____
If I'm broke Contact user 'TheDarkLordSano' via PM or IRC.

[I have a wiki page](https://www.reddit.com/r/HFY/wiki/tools/hfysubs)
"""

NEW_STORY_CONTENT = """
Hello {username}!

/u/{writer} just posted a new story called "{title}".

[Click here to read it]({url})

_____
^(To unsubscribe, send a message that contains the word unsubscribe and a list of users, for example: unsubscribe /u/username /u/username2)
_____
If I need to be bound and taught a lesson please contact 'TheDarkLordSano'. He Ties the knots just right.
"""

STALKER_NEW_CONTENT = """
Oh hello there {username},
 
It appears that someone we have been stalking together has posted something new.
 
/u/{writer} has posted something [scandalous]({url}).

[I have a wiki page](https://www.reddit.com/r/HFY/wiki/tools/hfysubs)
"""

IGNORE = ["Meta","meta","wp","video","text","misc","none","[Meta]","[WP]","[WPW]","[misc]","[MISC]","[video]","[text]"]
stalkers= ["fineillstoplurking","j1xwnbsr","someguynamedted","dejers","nine_tailed_smthng"]
#USERNAME = ""
#PASSWORD = ""


DATABASE = 'subs.db'

BROKER = 'pyamqp://guest@localhost//'
WRITE_POST_RATE_LIMIT = '60/m'
WRITE_PM_RATE_LIMIT = '60/m'

print('Loading SQL database')
sql = sqlite3.connect(DATABASE)
print('Connected to SQL database')
cur = sql.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS `notifications` (`id` int AUTO_INCREMENT PRIMARY KEY,`reddit_id` varchar(20) NOT NULL,`done` int(11) NOT NULL DEFAULT `0`)')
cur.execute('CREATE TABLE IF NOT EXISTS `repliedto` (`id` int AUTO_INCREMENT PRIMARY KEY,`reddit_id` varchar(10) NOT NULL,`user` varchar(50) NOT NULL,`replied_id` varchar(10) NOT NULL,`timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,`sub` varchar(50) NOT NULL DEFAULT `HFY`)')
cur.execute('CREATE TABLE IF NOT EXISTS `subscriptions` (`subscription_id` int AUTO_INCREMENT ,`subscribed_to` varchar(80) NOT NULL,`subscriber` varchar(80) NOT NULL,`subreddit` varchar(200) NOT NULL,`subscribe_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY (`subscription_id`),UNIQUE (`subscribed_to`,`subscriber`,`subreddit`))')
sql.commit()
sql.close()

def connect(): #connecting for every query? wow..
    db_connection = sqlite3.connect(DATABASE)
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
    cursor.execute('SELECT subscribed_to FROM subscriptions WHERE subscriber="%s" ORDER BY subscribed_to' % subscriber)
    items = cursor.fetchall()
    db_connection.close()
    return items
   
def get_subscribers(writer):
    db_connection = connect()
    cursor = db_connection.cursor()
    cursor.execute('SELECT subscriber FROM subscriptions WHERE subscribed_to="%s" COLLATE NOCASE' % writer)
    items = cursor.fetchall()
    db_connection.close()
    return items
    
def remove_subscription(writer, subscriber):
    db_connection = connect()
    cursor = db_connection.cursor()
    try:
        cursor.execute('DELETE FROM subscriptions WHERE subscribed_to="%s" AND subscriber="%s" AND subreddit="%s" COLLATE NOCASE' % (writer, subscriber, SUBREDDIT))
        db_connection.commit()
    except:
        print "Something went wrong when removing subscription to the database. Subscription possibly doesn't exists."
        db_connection.rollback()
    db_connection.close()
    
def add_subscription(writer, subscriber):
    db_connection = connect()
    cursor = db_connection.cursor()
    try:
        cursor.execute('INSERT INTO subscriptions(subscribed_to, subscriber, subreddit) VALUES("%s", "%s", "%s")' % (writer, subscriber, SUBREDDIT))
        db_connection.commit()
    except:
        print "Something went wrong when adding subscription to the database. Subscription possibly already exists."
        print "writer: %s subscriber: %s subreddit: %s" % (writer, subscriber, SUBREDDIT)
        db_connection.rollback()
    db_connection.close()

def clear_subscriptions(subscriber):
    db_connection = connect()
    cursor = db_connection.cursor()
    try:
        cursor.execute('DELETE FROM subscriptions WHERE subscriber="%s" AND subreddit="%s" COLLATE NOCASE' % (subscriber, SUBREDDIT))
        db_connection.commit()
    except:
        print "Something went wrong when removing subscription to the database. Subscription possibly doesn't exists."
        db_connection.rollback()
    db_connection.close()
