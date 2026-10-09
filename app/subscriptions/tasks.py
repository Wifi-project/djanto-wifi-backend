from celery import shared_task,group
from celery.utils.log import get_task_logger
from .models import  Microtik
from django.utils import timezone
from datetime import timedelta
from app.microtiks.services import check_connexion
from django.core.mail import send_mail
# from django.conf import settings
from app.utils.wg import disable_expired_subscriptions
from app.microtiks.gms import gdms_service
from asgiref.sync import async_to_sync

from config import settings

from app.transactions.models import (
    Transaction,
    )
from app.utils.wg import create_wg_user
from app.commone.tasks import send_async_email_task

logger = get_task_logger(__name__)

# =====================================================================
#  TÂCHE ASYNCHRONE (Déclenchée manuellement depuis tes API Views)
# =====================================================================

@shared_task(
        name='subscriptions.tasks.clock_expire_subscription_task',
        bind=True,
        autoretry_for=(Exception,),
        max_retries=3,
        default_retry_delay=60
)
def clock_expire_subscription_task(self):
    """Tache pour blocker les microtiks qui nont plus d'abonnements"""
    clients_expired = Microtik.objects.filter(
        admin_blocked=False,
        subscriptionwg__isnull=False,
        subscriptionwg__expire_at__lte = timezone.now(),
        ).select_related("subscriptionwg")

    
    success_count = 0
    errors_count = 0

    for expired in clients_expired:
        subscription = expired.subscriptionwg
        try:
            async_to_sync(gdms_service.block_unblock_ssid)(
                network_id=subscription.gdms_network_id,
                ssid_id=subscription.gdms_site_id,
                current_ssid_name=subscription.microtik.name.replace(' ','-'),
                block=True
                )
            # disable_expired_subscriptions(expired.subscriptionwg.wg_ip)

            expired.is_online = False
            expired.save(update_fields=['is_online'])
            success_count +=1

            subscription.is_active = False
            subscription.save(update_fields=['is_active'])

        except Exception as e:
            errors_count +=1
            send_async_email_task.delay(
                        subject="Alerte : Erreur de blocage",
                        message=(
                            f"Bonjour Mr Dounoh,\n\n"
                            f"Le blocage du microtik {expired.name} pour la fin de l'abonnement a echouer pour des raisons : {e}"
                            f"Veuillez verifier le systeme pour resoudre le probleme."
                        ),
                        recipient_list=[settings.ADMIN_EMAIL],
                    )

    if errors_count > 0:
        raise self.retry(
        exc=Exception(
            f"{errors_count} désactivations ont échoué sur wg-easy."
        )
    )




@shared_task(name='subscriptions.tasks.send_expiration_alerts_task')
def send_expiration_alerts_task():
    """ La tache pour envoyer des notifications de fin d'abonnement """
    today = timezone.now()
    in_5_days = today + timedelta(days=5)

    alert_clients = Microtik.objects.filter(
        admin_blocked=False,
        subscriptionwg__isnull=False,
        subscriptionwg__expire_at__gt=today,  
        subscriptionwg__expire_at__lte=in_5_days, 
    ).select_related("subscriptionwg").prefetch_related('owners')

    for mkt in alert_clients:
        days_left = mkt.subscriptionwg.days_remaining
        send_async_email_task.delay(
            subject="Alerte : Expiration de votre abonnement",
            message=(
                f"Bonjour,\n\n"
                f"Votre abonnement sur le routeur '{mkt.name}' expire dans {days_left} jour(s). "
                f"Veuillez vous réabonner pour continuer à profiter du service."
            ),
            recipient_list=[r.email for r in mkt.owners.all()],
        )



@shared_task(name="subscriptions.tasks.daily_subscription_check_task")
def daily_subscription_check_task():
    """Tâche principale appelée par Celery Beat (ex: tous les jours à minuit).

    Exécute le blocage et l'alerte en parallèle grâce à Celery group.
    """
    logger.info(
        "[Celery Beat] Lancement de la vérification quotidienne des abonnements..."
    )

    job = group(
        clock_expire_subscription_task.s(), send_expiration_alerts_task.s()
    )
    job.apply_async()
    return "Tâches de blocage et d'alerte lancées en arrière-plan."



# =====================================================================
#  TÂCHE PLANIFIÉE (Appelée automatiquement par Celery Beat)
# =====================================================================

@shared_task(name="subscriptions.tasks.sync_all_routers_task")
def sync_all_routers_task():
    """
    Tâche planifiée pour synchroniser TOUS les routeurs actifs du réseau.
    """
    microtiks = Microtik.objects.filter(
        admin_blocked=False,
        subscriptionwg__isnull=False,
        subscriptionwg__expire_at__gte=timezone.now(),
    ).select_related("subscriptionwg").prefetch_related('owners')
    
    list_info = []
    total = 0
    for routeur in microtiks:
        total += 1
        sub = routeur.subscriptionwg
        
        response = async_to_sync(gdms_service.list_voucher)(
            network_id=sub.gdms_network_id,
            page_num=1, page_size=10
        )
        if response:
            owner_emails = [r.email for r in routeur.owners.all()]
            send_async_email_task.delay(
                subject="Alerte : Déconnexion Routeur MikroTik",
                message=f"Votre routeur {routeur.name} ne répond plus via le VPN WireGuard. Veuillez vérifier s'il est allumé.",
                recipient_list=owner_emails
            )
            list_info.append({
                "microtik": routeur.name, 
                "owner": routeur.owners.first(), 
                "owner_email": owner_emails
            })
            routeur.is_online = False
            routeur.save(update_fields=['is_online'])
        else:
            routeur.is_online = True
            routeur.save(update_fields=["is_online"])

    # Envoi du rapport global à l'administrateur
    return send_async_email_task.delay(
        subject="Rapport : Vérification des MikroTiks",
        message=f"Vous avez {len(list_info)} microtik(s) sur {total} hors ligne: \n {list_info}",
        recipient_list=[settings.ADMIN_EMAIL]
    )



@shared_task(
    name="subscriptions.tasks.subscription_webhook_task",
    bind= True,
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=60,
    retry_backoff=True
)
def subscription_webhook_task(data: dict):
    """Callback après paiement"""
    ...
#     try:
#         payload = data.get('data',{})
#         reference = payload.get("merchantPaymentReference", "")

#         paiement = PaidSubscription.objects.get(slug=reference)

#         if paiement and paiement.status in [PaidSubscription.SUCCESS, PaidSubscription.FAILLED]:
#             return {"status": "Failled", "message": "Paiement deja traiter"}
        
#         paiement.status = PaidSubscription.SUCCESS
#         paiement.save()
        
#         expire_at = timezone.now().date() + timedelta(days=paiement.duration_days)
        
#         subscriptionwg = None
#         if paiement.subscription:
#             subscriptionwg = paiement.subscription

#         wg_username = subscriptionwg.slug if subscriptionwg else f"user_{payload}"
        
#         wg_result = create_wg_user(wg_username)
        
#         if wg_result.get('status') == "success":
#             client = wg_result.get('data', {})
            
#             if subscriptionwg:
#                 subscriptionwg.expire_at = expire_at
#                 subscriptionwg.is_active = True
#                 subscriptionwg.wg_client_id = client.get("id")
#                 subscriptionwg.wg_ip = client.get("address")
#                 subscriptionwg.wg_private_key = client.get("privateKey")
#                 subscriptionwg.wg_public_key = client.get("publicKey")
                
#                 subscriptionwg.save()
        
#         return {"status": "success", "message": "Paiement confirmé et VPN configuré"}

#     except Exception as e:
#         send_async_email_task.delay(
#             subject="Alerte : Erreur du webhook de subcription",
#             message=(
#                 f"Bonjour Mr Dounoh,\n\n"
#                 f"Erreur de la finalisation de la subscription de l'abonnement ID {reference} a echouer pour des raisons : {e}"
#                 f"Veuillez verifier le systeme pour resoudre le probleme."
#             ),
#             recipient_list=[settings.ADMIN_EMAIL],
#         )





