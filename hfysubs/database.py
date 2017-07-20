from django.conf import settings
import settings as app_settings

if not settings.configured:
    settings.configure(app_settings)

from django.db import models
from .models import subs, repto

Database = {
    subscriptions,
    repliedto
}