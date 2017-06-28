from __future__ import absolute_import
import re

from celery.utils.log import get_task_logger

from beetusbot import config
from .reddit import make_reddit
from .tasks.reddit_writer import send_message

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
                logger("Removing subscription from %s to %s" % (user, message.author))
                config.remove_subscription(user, message.author)

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
                    logger("Added subscription from %s to %s" % (user, message.author))
                    config.add_subscription(user, message.author)

            send_message.delay(
                str(message.author),
                "Your Current Subscriptions",
                construct_pm(
                    message.author,
                    "subscribed to",
                    users,
                    config.get_subscriptions(message.author)
                )
            )

        message.mark_read()


def construct_pm(author, action, users, subscriptions):
    """
    :type author: str
    :type action: str
    :type users: str[]
    :type subscriptions: (str)[]

    :rtype: str
    """

    subscriptions = [subscription[0] for subscription in subscriptions]
    if len(subscriptions) >= 1:
        subscriptions[0] = "* /u/" + subscriptions[0]
        userlist = "\n\n* /u/".join(subscriptions)

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
