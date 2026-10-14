# from celery import shared_task,group
# from celery.utils.log import get_task_logger
# from .models import  Microtik
# from django.core.mail import send_mail
# from config import settings
# from asgiref.sync import async_to_sync

# from app.microtiks.gms import GdmsService,provision_gdms

# logger = get_task_logger(__name__)


# @shared_task(
#         name='microtiks.tasks.provision_gdms_task',
#         bind=True,
#         autoretry_for=(Exception,),
#         max_retries=3,
#         default_retry_delay=60
#         )
# def provision_gdms_task(
#     self, 
#     network_name:str,
#     mac:str, 
#     ap_password:str, 
#     device_name:str, 
#     ssid_name:str, 
#     subwg_slug:str
#     ):
#     try:
#         return async_to_sync(provision_gdms)(
#                     network_name, 
#                     mac, 
#                     ap_password, 
#                     device_name, 
#                     ssid_name,
#                     subwg_slug
#                 )
#     except Exception as exc:
#         raise self.retry(exc=exc, countdown=10)