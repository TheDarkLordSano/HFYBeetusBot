from django.db import models


class repliedto(models.Model):
    id = models.AutoField(primary_key=True)
    reddit_id = models.CharField(max_length=20)
    author = models.CharField(max_length=20)
    replied_id = models.CharField(max_length=20)
    timest = models.DateTimeField(auto_now_add=True)
    sub = models.CharField(max_length=50)

    class Meta:
	db_table = 'repliedto'