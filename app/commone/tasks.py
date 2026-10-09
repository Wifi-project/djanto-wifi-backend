from celery import shared_task,group
from celery.utils.log import get_task_logger
from django.core.mail import send_mail
from config import settings

logger = get_task_logger(__name__)



@shared_task(
    name="subscriptions.tasks.send_async_email_task",
    bind=True,
    autoretry_for=(Exception,), 
    max_retries=3,
    retry_backoff=True
)
def send_async_email_task(self, subject: str, message: str, recipient_list: list):
    """
    Tâche asynchrone générique pour envoyer des e-mails sans bloquer l'application.
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(recipient_list),
            fail_silently=False,  
        )
        return f"Email envoyé à {recipient_list}"
        
    except Exception as e:
        raise e  