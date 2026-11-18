from app.transactions.models import Transaction,TransactionType
from django.db.models import Q
from app.utils.pagination import paginate_queryset
from ninja.errors import HttpError
from app.api_extern.djomy import DjomyClient
from app.utils.enum import WebhookEvent
from app.transactions.tasks import webhook
from asgiref.sync import async_to_sync


def list_transaction_log(search:str,status:str,page_num:int,page_size:int,type=str):
    qs = Transaction.objects.select_related("network", "profil", "category").order_by("-created_at")
    
    if search:
        qs = qs.filter(
            Q(transaction_id__icontains=search) |
            Q(phone_number__icontains=search)   |
            Q(network_name__icontains=search)
        )
    if status:
        qs = qs.filter(status=status)
    if type:
        qs = qs.filter(type=type)

    return paginate_queryset(qs, page_num, page_size)



def list_subscriptions_for_network(network):
    return Transaction.objects.filter(
        network=network,
        type__in=[TransactionType.CONFIGURATION,TransactionType.SUBSCRIPTION,TransactionType.SUBSCRIPTION_RENEWAL],
    )[:5]



def log_transactions_for_owner_network(
    network,
    search: str,
    status: str,
    page_num: int,
    page_size: int,
):
    qs = Transaction.objects.filter(
        network=network,
        type__in=[TransactionType.VOUCHER_PURCHASE],
    ).order_by('-created_at')

    if search:
        qs = qs.filter(phone_number__icontains=search)   

    if status:
        qs = qs.filter(status=status)                    

    return paginate_queryset(qs=qs, page_size=page_size, page_num=page_num)




def handle_transaction_webhook(signature_header: str, data: dict):
    try:
        version_prefix, received_signature = signature_header.split(":")
    except ValueError:
        raise HttpError(400, "Format de signature invalide")

    hmac = DjomyClient()
    async_to_sync(hmac.webhook_signature_check)(received_signature=received_signature)
    
    event_type = data.get("eventType")
    event_id = data.get("eventId")
    webhook_data = data.get("data", {})

    # Appel direct (puisque tu as retiré @shared_task pour tester)
    return webhook(
        event_type=event_type,
        webhook_data=webhook_data
    )

    print(f"Webhook reçu : {event_type} (ID: {event_id})")

    # return {'status': 'success', 'message': 'Webhook reçus avec succès.'}