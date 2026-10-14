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
    
#     """
#     Webhook de notification de paiement.
#     Gère la validation du paiement, la création du ticket sur le MikroTik
#     et la mise à jour de la base de données.
#     """

#     event_id = data.get("eventId", "")
#     data_transaction = data.get("data", {})
#     reference = data_transaction.get("merchantPaymentReference", "")
#     transactionId = data_transaction.get("transactionId", "")
#     status = data_transaction.get("status", "")

#     deposit = InfoDeposit.objects.select_related("microtik").filter(slug=reference).first()
    
#     if not deposit:
#         return {"status": "error", "message": "Transaction introuvable"}

#     if deposit.status in [InfoDeposit.SUCCESS, InfoDeposit.FAILED]:
#         return {"status": "ignored", "message": "Transaction déjà traitée"}

#     microtik = deposit.microtik

#     if status == "SUCCESS":
        
#         get_code = generer_code_unique(longueur=10)
#         while Client.objects.filter(code_username=get_code, microtik=microtik).exists():
#             get_code = generer_code_unique(longueur=10)  

#         current_time_str = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        
#         create_user_api = creer_ticket_code(
#             microtik=microtik,
#             code_paye=get_code,
#             profile=deposit.profil_name,
#             limit_uptime=deposit.limit_uptime,
#             comment=f"Date: {current_time_str} Paye via Djanto wifi"
#         )

#         if create_user_api.get('status') is True:
#             try:
#                 with transaction.atomic():
#                     deposit_lock = InfoDeposit.objects.select_for_update().get(id=deposit.id)
                    
#                     Client.objects.create(
#                         phone_number=deposit_lock.number_receve_code,
#                         code_username=get_code,
#                         code_password=get_code,
#                         microtik=microtik,
#                         info_deposit=deposit_lock,
#                         limit_uptime=deposit_lock.limit_uptime,
#                         profil_name=deposit_lock.profil_name,
#                         transactionId=transactionId
#                     )

#                     deposit_lock.status = InfoDeposit.SUCCESS
#                     deposit_lock.eventId = event_id
#                     deposit_lock.save()

#                     microtik.sold += deposit_lock.amount
#                     microtik.users += 1
#                     microtik.save()
                
#                 # --- 5. ENVOI DU SMS ---
#                 # À déclencher de préférence via une tâche Celery en tâche de fond ici
#                 # exemple_task_sms.delay(deposit_lock.number_receve_code, get_code)

#                 return {"status": "success", "message": "Ticket créé et BDD mise à jour avec succès"}

#             except Exception as e:
#                 return {"status": "error", "message": "Erreur interne de base de données"}
        
#         else:
            
#             deposit.status = InfoDeposit.FAILED
#             deposit.eventId = event_id
#             # Si tu as un champ de note ou de log d'erreur sur ton modèle, tu peux l'ajouter ici :
#             # deposit.error_log = f"Erreur MikroTik : {create_user_api.get('message')}"
#             deposit.save()
            
#             return {"status": "failed", "message": "Paiement validé mais échec de création sur le routeur"}


#     else:
#         deposit.status = InfoDeposit.FAILED
#         deposit.eventId = event_id
#         deposit.save()
        
#         return {"status": "failed", "message": "Le paiement a échoué chez l'opérateur"}
            
