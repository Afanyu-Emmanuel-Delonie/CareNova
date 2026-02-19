import os
from celery import Celery

# 1. Set the default Django settings module for the 'celery' program.
# Change 'backend' to your actual folder name if it is different
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('CareNova')
.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
