from celery import shared_task
from app.commone.tasks import sender_email
from config import settings
from app.transactions.models import Transaction,TransactionType,TransactionStatus
from app.utils.enum import WebhookEvent
from django.db import transaction as db_transaction
from celery.exceptions import MaxRetriesExceededError



# # @shared_task(
# #     bind=True,
# #     autoretry_for=(Exception,), 
# #     retry_kwargs={'max_retries': 3},  
# #     retry_backoff=5,  
# #     retry_jitter=True 
# # )
# def webhook(self, event_type, webhook_data: dict):
#     from app.subscriptions.services import ( 
#         return_url_config_service,
#         return_url_subscription_service,
#     )
#     from app.clients.services import webhook_voucher

#     payment_info = webhook_data.get("payment") or webhook_data.get("payout") or {}
#     transaction_id = payment_info.get("transactionId") or payment_info.get("payoutId")
    
#     if not transaction_id:
#         return {"status": "error", "message": "Transaction ID manquant"}

#     raw_status = payment_info.get("status")
#     if raw_status in ["SUCCESS", "COMPLETED"]:
#         new_status = TransactionStatus.COMPLETED
#     elif raw_status in ["FAILED", "REJECTED"]:
#         new_status = TransactionStatus.FAILED
#     else:
#         new_status = TransactionStatus.PENDING

#     receivedAmount = payment_info.get("receivedAmount")

#     try:
#         with db_transaction.atomic():
#             transaction = (
#                 Transaction.objects
#                 .select_for_update()
#                 .filter(transaction_id=transaction_id)
#                 .select_related("category", "network", "profil")
#                 .first()
#             )
            
#             if not transaction:
#                 return {"status": "error", "message": "Transaction introuvable en base"}

#             if transaction.status in [TransactionStatus.COMPLETED, TransactionStatus.FAILED]:
#                 print(f"⚠️ Webhook en double ignoré pour la transaction {transaction_id} (Déjà {transaction.status})")
#                 return {"status": "ignored", "message": "Transaction déjà traitée (idempotence respectée)"}

#             transaction.status = new_status
#             if receivedAmount is not None:
#                 transaction.receivedAmount = receivedAmount
            
#             transaction.save(update_fields=['status', 'receivedAmount'])

#             if new_status == TransactionStatus.COMPLETED:
#                 transaction_type = transaction.type

#                 if transaction_type == TransactionType.CONFIGURATION:
#                     return_url_config_service(transaction=transaction)

#                 elif transaction_type == TransactionType.SUBSCRIPTION:
#                     return_url_subscription_service(
#                         network=transaction.network,
#                         transaction=transaction
#                     )

#                 elif transaction_type == TransactionType.VOUCHER_PURCHASE:
#                     webhook_voucher(transaction)

#     except Exception as exc:
#         print(f"❌ Erreur lors du traitement du webhook pour {transaction_id}: {exc}")
#         # Déclenche la relance Celery selon les paramètres définis au dessus
#         raise self.retry(exc=exc)

#     return {"status": "success", "message": "Webhook traité avec succès"}



def webhook(event_type, webhook_data: dict):
    from app.subscriptions.services import ( 
        return_url_config_service,
        return_url_subscription_service,
    )
    from app.clients.services import webhook_voucher

    payment_info = webhook_data.get("payment") or webhook_data.get("payout") or {}
    transaction_id = payment_info.get("transactionId") or payment_info.get("payoutId")
    
    if not transaction_id:
        return {"status": "error", "message": "Transaction ID manquant"}

    raw_status = payment_info.get("status")
    if raw_status in ["SUCCESS", "COMPLETED"]:
        new_status = TransactionStatus.COMPLETED
    elif raw_status in ["FAILED", "REJECTED"]:
        new_status = TransactionStatus.FAILED
    else:
        new_status = TransactionStatus.PENDING

    receivedAmount = payment_info.get("receivedAmount")

    try:
        with db_transaction.atomic():
            transaction = (
                Transaction.objects
                .select_for_update()
                .filter(transaction_id=transaction_id)
                .select_related("category", "network", "profil")
                .first()
            )
            
            if not transaction:
                return {"status": "error", "message": "Transaction introuvable en base"}

            # Règle d'idempotence
            if transaction.status in [TransactionStatus.COMPLETED, TransactionStatus.FAILED]:
                print(f"⚠️ Webhook en double ignoré pour la transaction {transaction_id} (Déjà {transaction.status})")
                return {"status": "ignored", "message": "Transaction déjà traitée (idempotence respectée)"}

            transaction.status = new_status
            if receivedAmount is not None:
                transaction.receivedAmount = receivedAmount
            
            transaction.save(update_fields=['status', 'receivedAmount'])

            if new_status == TransactionStatus.COMPLETED:
                transaction_type = transaction.type

                if transaction_type == TransactionType.CONFIGURATION:
                    return_url_config_service(transaction=transaction)

                elif transaction_type == TransactionType.SUBSCRIPTION:
                    return_url_subscription_service(
                        network=transaction.network,
                        transaction=transaction
                    )

                elif transaction_type == TransactionType.VOUCHER_PURCHASE:
                    webhook_voucher(transaction)

    except Exception as exc:
        print(f"❌ Erreur lors du traitement du webhook pour {transaction_id}: {exc}")
        # En synchrone pur, on relève l'exception pour que Django/le client voie l'erreur
        raise exc

    return {"status": "success", "message": "Webhook traité avec succès"}