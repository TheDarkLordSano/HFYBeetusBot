from __future__ import absolute_import
import re

from celery.utils.log import get_task_logger

from beetusbot import config
from .reddit import make_reddit
from .tasks.reddit_writer import send_message
from .models.subs import Subscriptions
from django.db import IntegrityError

logger = get_task_logger(__name__)

user_regex = re.compile('\/([A-Za-z0-9_-]{1,})')  # user regex


def extract_users(message):
    return user_regex.findall(message)


def handle_inbox_stream():
    reddit = make_reddit()

    for message in reddit.inbox.stream():
        if "unsubscribe" in message.body.lower() or "unsubscribe" in message.subject.lower():
            users = extract_users(message.body)
            for user in users:
                logger.info("Removing subscription from %s to %s" % (user, message.author))
		Subscriptions.objects.filter(subscribed_to__iexact=user, subscriber=message.author).delete()


            send_message.delay(
                str(message.author),
                "Your Current Subscriptions",
                construct_pm(
                    message.author,
                    "unsubscribed from",
                    users,
                    config.get_subscriptions(message.author)
                )
            )
        elif "subscribe" in message.body.lower() or "subscribe" in message.subject.lower():
            users = extract_users(message.body)
            for user in users:
                if user.lower() == 'u':
                    continue
                else:
                    logger.info("Added subscription from %s to %s" % (user, message.author))
		    try:
			Subscriptions.create(subscriber=message.author, subscribed_to=user)
		    except IntegrityError as e:
		        if 'unique constraint' in e.args[0]:
			    logger.info("Subscription does not exist")
			    continue

            send_message.delay(
                str(message.author),
                "Your Current Subscriptions",
                construct_pm(
                    message.author,
                    "subscribed to",
                    users,
                    list(Subscriptions.filter(subscriber=message.author).values_list("subscribed_to",flat=True))
                )

            )

        message.mark_read()
'''
  values_list returns the given model field(s). Flat being true turns this into a list.
  Flat CANNNOT be used with multiple fields.
'''

def construct_pm(author, action, users, sublist):
    """
    :type author: str
    :type action: str
    :type users: str[]
    :type subscriptions: (str)[]

    :rtype: str
    subscriptions = [subscription[0] for subscription in subscriptions]
    """
    if len(sublist) >= 1:
        sublist[0] = "* /u/" + sublist[0]
        userlist = "\n\n* /u/".join(sublist)

        return config.SUBSCRIPTION_CONTENT.format(
            username=author,
            action=action,
            users=' '.join(users),
            subscriptions=userlist
        )
    else:
        return config.SUBSCRIPTION_CONTENT.format(
            username=author,
            action=action,
            users=' '.join(users),
            subscriptions="You don't have any subscriptions"
        )
