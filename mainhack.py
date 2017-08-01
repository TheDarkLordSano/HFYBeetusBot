from __future__ import absolute_import, unicode_literals

from multiprocessing import Process, TimeoutError

from hfysubs import inboxhack


if __name__ == "__main__":
    #submissions = Process(target=submissions.handle_subscription_stream())
    inbox = Process(target=inboxhack.handle_inbox)

    #submissions.start()
    inbox.start()

    # Flip between our two worker processes ensuring they are both still running
    # if one dies, kill the other and terminate the application to provide better
    # feedback to the user running the bot