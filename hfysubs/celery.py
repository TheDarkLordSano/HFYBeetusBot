from __future__ import absolute_import, unicode_literals
from celery import Celery, Task

from .reddit import make_reddit
from .settings import BROKER

app = Celery('hfysubs',
             broker=BROKER,
             include=['hfysubs.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)


class RedditTask(Task):
    """
    This Celery Task is to ensure that every worker has its own copy of praw.Reddit
    as the praw library is not thread-safe
    https://praw.readthedocs.io/en/latest/getting_started/multiple_instances.html
    """

    _reddit = None

    @property
    def reddit(self):
        if self._reddit is None:
            self._reddit = make_reddit()
        return self._reddit

if __name__ == '__main__':
    app.start()
