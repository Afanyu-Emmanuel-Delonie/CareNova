import os
from celery import Celery

# 1. Set the default Django settings module for the 'celery' program.
# Change 'backend' to your actual folder name if it is different
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('CareNova')

# 2. Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
