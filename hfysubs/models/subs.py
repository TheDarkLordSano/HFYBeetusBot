from django.db import models


class Subscriptions(models.Model):
    id = models.AutoField(primary_key=True)
    subscribed_to = models.CharField(max_length=80)
    subscriber = models.CharField(max_length=80)
    subreddit = models.CharField(max_length=200)
    subscribe_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            ('subscribed_to', 'subscriber', 'subreddit')
        )
	db_table = 'subscriptions'