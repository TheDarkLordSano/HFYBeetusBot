'''
Created on Oct 5, 2013
@author: Chris
Edited 4/24/2015 
@additions: TheDarkLordSano
'''

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

"""

SUBSCRIPTION_CONTENT = """
Hello there {username}!

You have been {action} {users}

Your current subscriptions are now:
{subscriptions}

_____
^(To unsubscribe to any of these users, send a message that contains the word unsubscribe and a list of users, for example: unsubscribe /u/username /u/username2)

[I have a wiki page](https://www.reddit.com/r/HFY/wiki/tools/hfysubs)
"""

NEW_STORY_CONTENT = """
Hello {username}!

/u/{writer} just posted a new story called "{title}".

[Click here to read it]({url})

_____
^(To unsubscribe, send a message that contains the word unsubscribe and a list of users, for example: unsubscribe /u/username /u/username2)
"""

IGNORE = ["Meta","meta","wp","video","text","misc","none","[Meta]","[WP]","[WPW]","[misc]","[MISC]","[video]","[text]"]


BROKER = 'pyamqp://guest@localhost//'
WRITE_POST_RATE_LIMIT = '60/m'
WRITE_PM_RATE_LIMIT = '60/m'
