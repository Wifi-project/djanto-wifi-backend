import os
from celery import Celery
from celery.schedules import crontab

# 1. On indique à Django où se trouve son fichier settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 2. On nomme l'application Celery avec juste 'config'
app = Celery('config')

# 3. On charge les variables commençant par CELERY_ depuis settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# 4. Import explicite des modules contenant des tâches
app.conf.imports = (
    'app.clients.tasks',
    'app.subscriptions.tasks',
)

# 5. Planning Celery Beat
app.conf.beat_schedule = {
    'sync-database-with-mikrotik-every-1-hour': {
        'task': 'clients.tasks.sync_all_routers_task', 
        'schedule': crontab(minute='0', hour='*')
    },
    # 'tache-chaque-jour-a-minuit': {
    #     'task': 'subscriptions.tasks.daily_subscription_check_task',
    #     'schedule': crontab(minute='0', hour='0'), 
    # },
    'tache-chaque-jour-a-minuit': {
        'task': 'subscriptions.tasks.daily_subscription_check_task',
        'schedule': crontab(minute='*'),  # Se déclenche toutes les minutes
    },
}


# 6. Auto-détection des tâches dans vos apps Django
app.autodiscover_tasks()