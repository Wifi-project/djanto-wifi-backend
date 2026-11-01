from django.db import models
from app.gdms.models import Profil,Network
from app.subscriptions.models import SubscriptionCategorie
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
    network = models.ForeignKey(
        Network, on_delete=models.CASCADE, 
        related_name='microtik_transactions', 
        related_query_name='microtik_transaction',
        null=True
        )
    network_name = models.CharField(max_length=250, null=True)
    network_description = models.CharField(max_length=250, null=True,blank=True)
    profil = models.ForeignKey(
        Profil,
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        )
    category = models.ForeignKey(
        SubscriptionCategorie, 
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



class PaymentMethod(Base):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom",
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Code",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name        = "Moyen de transaction"
        verbose_name_plural = "Moyens de transaction"
        ordering            = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"