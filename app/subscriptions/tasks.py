from celery import shared_task,group
from celery.utils.log import get_task_logger
from app.gdms.models import Network,Gdms,Status
from django.utils import timezone
from datetime import timedelta
from app.commone.tasks import sender_email
from app.gdms.api_gdms import gdms_service
from asgiref.sync import async_to_sync
from api_extern.nimba_sms import send_sms
from config import settings


logger = get_task_logger(__name__)

# # =====================================================================
# #  TÂCHE ASYNCHRONE (Déclenchée manuellement depuis tes API Views)
# # =====================================================================

@shared_task(
    name='subscriptions.tasks.alerte_and_suspend_abonnement_task',
    bind=True,
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=60
)
def alerte_and_suspend_abonnement_task(self):
    """Tache pour bloquer les réseaux qui n'ont plus d'abonnements"""
    clients_expired = Network.objects.filter(
        admin_blocked=False,
        status = Status.ACTIVE,
        subscription_expire_at__lte=timezone.now().date() + timedelta(days=7),
    ).prefetch_related("owners")
    
    success_count = 0
    errors_count = 0

    for expired in clients_expired:
        owners = [{
            'full_name': f'{owner.first_name} {owner.last_name}',
            'number': owner.phone_number
        } for owner in expired.owners.all()]

        days_remaining = expired.days_remaining
        nom_reseau = expired.name

        if days_remaining == 1 or days_remaining == 3 or days_remaining == 7:
            for owner in owners:
                num = owner.get("number")
                if num:
                    async_to_sync(send_sms.send)(
                        number=str(num),
                        message=(
                            f"Bonjour {owner.get("full_name")}, il vous reste {days_remaining} jours d'abonnement pour le réseau {nom_reseau}. "
                            f"Pensez à vous réabonner pour continuer à profiter de nos services. - L'équipe Djantowifi"
                        )
                    )

        try:
            if days_remaining == 0:
                async_to_sync(gdms_service.block_unblock_ssid)(
                    network_id=expired.network_id,
                    ssid_id=expired.site_id,
                    current_ssid_name=nom_reseau,
                    block=True
                )

                expired.status = Status.DISABLE
                expired.save(update_fields=['status'])
                
                message_blocage = (
                    f"Bonjour votre abonnement pour le réseau {nom_reseau} a expiré. "
                    f"Le réseau a été suspendu. Réabonnez-vous pour rétablir l'accès. - L'équipe Djantowifi"
                )
                
                for owner in owners:
                    num = owner.get("number")
                    if num:
                        async_to_sync(send_sms.send)(
                            number=str(num),
                            message=message_blocage
                        )
                
        except Exception as e:
            errors_count += 1
            sender_email(
                subject='Erreur sur les blocage network abonnement',
                message=f"Erreur lors du blocage du réseau {nom_reseau} : {e}",
                recipient_list=[settings.ADMIN_EMAIL]
            )

    if errors_count > 0:
        raise self.retry(
            exc=Exception(
                f"{errors_count} désactivations ont échoué."
            )
        )
    
    return f"Tâche exécutée avec succès. Succès : {success_count}, Erreurs : {errors_count}"




