import os

from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_q.models import Schedule
from django_q.tasks import async_task, schedule

from .models import Peraturan
# from .tasks import run_populate_body_text


# @receiver(post_save, sender=Peraturan)
# def body_text_handler(sender, instance, **kwargs):
#     async_task(
#         "jdih.tasks.run_populate_body_text",
#         sync=os.name == "nt",
#     )
#     schedule(
#         run_populate_body_text,
#         sync=os.name == "nt",
#         schedule_type=Schedule.ONCE,
#         next_run=timezone.now() + timedelta(minutes=1),
#     )
