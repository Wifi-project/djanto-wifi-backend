# from celery import shared_task
# from django.db import transaction
# from django.utils import timezone
# from app.clients.models import InfoDeposit,Client
# from app.utils.def_utils import connect_microtik, generer_code_unique, creer_ticket_code


# @shared_task(
#     name="clients.tasks.process_payment_webhook_task",
#     bind=True, 
#     autoretry_for=(Exception,),
#     max_retries=3, 
#     default_retry_delay=30
# )
# def process_payment_webhook_task(self, data: dict):
    
