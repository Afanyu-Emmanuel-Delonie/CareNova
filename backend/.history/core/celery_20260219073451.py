import os
from celery import Celery

# Add this for Windows stability with eventlet
try:
    import eventlet
    eventlet.monkey_patch()
except ImportError:
    pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('CareNova')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()