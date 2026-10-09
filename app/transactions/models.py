from django.db import models
from app.microtiks.models import Microtik,Profil
from app.subscriptions.models import SubscriptionCategorieWg
from app.commone.models import Base


class TransactionStatus(models.TextChoices):
    """Statuts des transactions (abonnements, vouchers, retraits)"""
    
    PENDING = "pending", "En attente"
    PROCESSING = "processing", "En cours de traitement"
    COMPLETED = "completed", "Terminé"
    FAILED = "failed", "Échoué"
    CANCELLED = "cancelled", "Annulé"
    REFUNDED = "refunded", "Remboursé"
    EXPIRED = "expired", "Expiré"


class TransactionType(models.TextChoices):
    """Types de transactions"""
    CONFIGURATION = "configuration","prix de configuration"
    SUBSCRIPTION = "subscription", "Abonnement"
    SUBSCRIPTION_RENEWAL = "subscription_renewal", "Renouvellement d'abonnement"
    VOUCHER = "voucher", "Voucher"
    VOUCHER_PURCHASE = "voucher_purchase", "Achat de voucher"

    WITHDRAWAL_OWNER = "withdrawal_owner", "Retrait de gain par propriétaire"
    WITHDRAWAL_ADMIN = "withdrawal_admin", "Retrait de gain par admin système"
    WITHDRAWAL_MERCHANT = "withdrawal_merchant", "Retrait par marchand"
    
    DEPOSIT = "deposit", "Dépôt"
    COMMISSION = "commission", "Commission"
    REFUND = "refund", "Remboursement"


class Transaction(Base):  
    transaction_id = models.CharField(max_length=250,null=True)  
    phone_number = models.CharField(
        max_length=20, 
        null=True, blank=True
        )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2
        )
    microtik = models.ForeignKey(
        Microtik, on_delete=models.CASCADE, 
        related_name='microtik_transactions', 
        related_query_name='microtik_transaction'
        )
    profil = models.ForeignKey(
        Profil,
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        )
    category = models.ForeignKey(
        SubscriptionCategorieWg, 
        on_delete=models.PROTECT,
        related_name="category_transactions",
        null=True, 
        blank=True,
        )
    payment_method = models.CharField(
        max_length=250,
        null=False
    )
    type = models.CharField(
        max_length=50, 
        choices=TransactionType
        )
    status = models.CharField(
        max_length=50, 
        choices=TransactionStatus, 
        default=TransactionStatus.PENDING
        )
    
    def __str__(self):
        return f"Paiement {self.slug} - {self.status}"


