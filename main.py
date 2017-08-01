from __future__ import absolute_import, unicode_literals

from multiprocessing import Process, TimeoutError

from hfysubs import submissions, inbox


if __name__ == "__main__":
    submissions = Process(target=submissions.handle_subscription_stream())
    inbox = Process(target=inbox.handle_inbox_stream)

    submissions.start()
    #inbox.start()

    # Flip between our two worker processes ensuring they are both still running
    # if one dies, kill the other and terminate the application to provide better
    # feedback to the user running the bot
    running = True
    while running:
        try:
            submissions.join(10)
            running = False
        except TimeoutError:
            pass

        #try:
        #    inbox.join(10)
        #    running = False
        #except TimeoutError:
        #    pass

    if submissions.is_alive():
        submissions.terminate()

    if inbox.is_alive():
        inbox.terminate()
