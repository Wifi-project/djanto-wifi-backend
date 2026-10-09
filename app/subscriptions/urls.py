# app/subscriptions/urls.py
from ninja import Router
from ninja.pagination import LimitOffsetPagination, paginate
from ninja.errors import HttpError
from app.subscriptions.models import (
    SubscriptionCategorieWg,
    SubscriptioPriceBase,
    ConfigurationPrice,
    )
from app.subscriptions.schemas import (
    SubscriptionCategorieIntSchema,
    SubscriptionCategorieOutShema,
    SubscriptionCategorieUpdateSchema,
    SubscriptionWgInSchema,
    SubscriptionResponse,
    PriceBaseInt, 
    PriceBaseOut,
    PriceBaseUpdate,
    PaidSubscriptionListSchema,
    PaidSubscriptionDetailSchema,
    WebhookSchema,
    WebhookOutSchemas,
    SubscriptionWGupdateSchema,
    SubscriptionWGBaseSchema,
    ConfigurationInSchema
)
from app.users.models import User
from http import HTTPStatus
# from app.users.deps import , Auth, IsOwnerMicrotik, HasValidVpn
from app.subscriptions.services import (
    subscrition_abonnement_service,
    create_price_base_service,
    update_price_base_service,
    update_categorie_abonnement,
    create_categorie_abonnement,
    return_url,
    update_suscription_access,
    init_configuration,
)
from app.permissions.checker import PermissionsChecker
from app.permissions.enum_permissions import PermissionsEnum


subscription = Router(tags=["Subscription-WG"], auth=PermissionsChecker())

# ------------------ Le prix de base --------------------#

@subscription.post(
    "/price",
    response=PriceBaseOut,
    auth=PermissionsChecker(permissions=[PermissionsEnum.BASE_PRICE_CREATE]),
    tags=["Prix de base"],
    summary="Créer un prix de référence",
    description=(
        "Le prix de base est le prix qui sera automatiquement utilisé "
        "pour déterminer le prix total par abonnement. "
        "La formule de calcul est : **Prix total = Prix_base × Nombre_de_jours**.\n\n"
        "**Exemple :**\n"
        "- Prix_base = 15000\n"
        "- Durée = 30 jours\n"
        "- Prix total = 15000 × 30 = 450000\n\n"
        "⚠️ Il ne peut y avoir qu'un seul prix de base actif à la fois."
    )
)
def create_price_base(request, data: PriceBaseInt) -> PriceBaseOut:
    """
    Crée un nouveau prix de référence pour les abonnements.
    
    Args:
        data (PriceBaseInt): Données du prix (montant, devise, etc.)
    
    Returns:
        PriceBaseOut: Le prix créé avec ses détails
    """
    return create_price_base_service(data=data.model_dump())


@subscription.get(
    "/price",
    response=list[PriceBaseOut],
    tags=["Prix de base"],
    summary="Lister les prix de référence",
    description="Récupère la liste de tous les prix de base disponibles."
)
def get_price_base(request) -> list[PriceBaseOut]:
    """
    Retourne la liste des prix de base enregistrés.
    
    Returns:
        list[PriceBaseOut]: Liste des prix de base
    """
    return SubscriptioPriceBase.objects.all()


@subscription.patch(
    "/price/{slug}",
    response=PriceBaseOut,
    auth=PermissionsChecker(permissions=[PermissionsEnum.BASE_PRICE_UPDATE]),
    tags=["Prix de base"],
    summary="Modifier un prix de référence",
    description=(
        "Met à jour un prix de base existant.\n\n"
        "**Champs modifiables :**\n"
        "- `amount` : Montant du prix\n"
        "- `is_active` : Activer/désactiver le prix\n"
        "- `name` : Nom du prix\n"
        "- `description` : Description\n\n"
        "⚠️ Si le prix est désactivé, il ne sera plus utilisé pour les nouveaux abonnements."
    )
)
def update_price_base(request, data: PriceBaseUpdate, slug: str) -> PriceBaseOut:
    """
    Met à jour un prix de référence existant.
    
    Args:
        slug (str): Slug unique du prix à modifier
        data (PriceBaseUpdate): Nouvelles données du prix
    
    Returns:
        PriceBaseOut: Le prix mis à jour
    """
    return update_price_base_service(slug=slug, data=data.model_dump())


@subscription.get(
        '/price/configuration/',
        response=PriceBaseOut,
        tags=["Prix de base"],
        )
def configuration_price(request):
    return ConfigurationPrice.objects.first()
    

# ---------------------- Categorie Abonement ----------------------- #

@subscription.post(
    "/categories",
    response=SubscriptionCategorieOutShema,
    auth=PermissionsChecker(permissions=[PermissionsEnum.CATEGORY_CREATE]),
    tags=["Catégories"],
    summary="Créer une catégorie d'abonnement",
    description=(
        "Crée une nouvelle catégorie d'abonnement avec sa durée et son prix.\n\n"
        "**Règles :**\n"
        "- La durée totale est calculée automatiquement : `jours + (mois × 30)`\n"
        "- Le prix final est calculé à partir du prix de base actif\n"
        "- La remise est appliquée en pourcentage sur le prix de base\n\n"
        "**Exemple :**\n"
        "- name : '3 MOIS'\n"
        "- jours: 0, mois: 3\n"
        "- discount(remise/reduction) : 2.1\n"
        "- Prix : Prix_base × (1 - remise/100)"
    )
)
def create_category(request, data: SubscriptionCategorieIntSchema) -> SubscriptionCategorieOutShema:
    """
    Crée une nouvelle catégorie d'abonnement.
    
    Args:
        data (SubscriptionCategorieIntSchema): Données de la catégorie
    
    Returns:
        SubscriptionCategorieOutShema: La catégorie créée
    """
    return create_categorie_abonnement(data=data.model_dump())


@subscription.get(
    "/categories",
    response=list[SubscriptionCategorieOutShema],
    auth=PermissionsChecker(),
    tags=["Catégories"],
    summary="Lister les catégories d'abonnement",
    description=(
        "Récupère la liste des catégories d'abonnement.\n\n"
        "**Filtrage :**\n"
        "- **Admin** : Voir toutes les catégories (actives et inactives)\n"
        "- **Utilisateur standard** : Voir uniquement les catégories actives"
    )
)
@paginate(LimitOffsetPagination, page_size=10)
def get_categories(request) -> list[SubscriptionCategorieOutShema]:
    """
    Retourne la liste des catégories d'abonnement.
    
    Returns:
        list[SubscriptionCategorieOutShema]: Liste des catégories
    """
    user = request.user
    
    if user and user.user_type and user.user_type == User.ADMIN:
        return SubscriptionCategorieWg.objects.all()
    return SubscriptionCategorieWg.objects.filter(is_active=True)


@subscription.patch(
    "/categories/{slug}",
    response=SubscriptionCategorieOutShema,
    auth=PermissionsChecker(permissions=[PermissionsEnum.CATEGORY_UPDATE]),
    tags=["Catégories"],
    summary="Modifier une catégorie",
    description=(
        "Met à jour une catégorie d'abonnement existante.\n\n"
        "**Champs modifiables :**\n"
        "- `name` : Nom de la catégorie\n"
        "- `days` : Nombre de jours\n"
        "- `months` : Nombre de mois (converti en jours)\n"
        "- `discount` : Remise en pourcentage\n"
        "- `is_active` : Activer/désactiver la catégorie\n\n"
    )
)
def update_category(request, slug: str, data: SubscriptionCategorieUpdateSchema) -> SubscriptionCategorieOutShema:
    return update_categorie_abonnement(slug=slug, data=data.model_dump())


@subscription.delete(
    "/categories/{slug}",
    auth=PermissionsChecker(permissions=[PermissionsEnum.CATEGORY_DELETE]),
    tags=["Catégories"],
    summary="Supprimer une catégorie",
    description=(
        "Supprime définitivement une catégorie d'abonnement.\n\n"
        " **Attention :** les categories qui ont deja des abonnements ne pourrons pas etre effacé. "
    )
)
def delete_category(request, slug: str):
    try:
        category = SubscriptionCategorieWg.objects.get(slug=slug)
        if category.paid_subscription.exists():
            raise HttpError(
                status_code=404,
                message="Cette categorie a deja des abonnements."
            )
        
        category.delete()
        return {"success": True, "message": "Catégorie supprimée avec succès"}
    except SubscriptionCategorieWg.DoesNotExist:
        raise HttpError(404, "Catégorie non trouvée")


# ------------------------- Subscription -------------------------------#

@subscription.post(
        "/configuration/{microtik_slug}",
        auth=PermissionsChecker(permissions=[PermissionsEnum.SUBSCRIPTION_CONFIGURATION], owner=True),
        response=SubscriptionResponse,
        tags=['Abonnements'],
        description=(
            "la route pour payer les frais de configuration du routeur."
        )
)
async def configuration_routeur(request,microtik_slug, data:ConfigurationInSchema):
    return await init_configuration(
        data = data.model_dump(),
        microtik=request.microtik
    )


@subscription.post(
    "/{microtik_slug}",
    response=SubscriptionResponse,
    auth=PermissionsChecker(permissions=[PermissionsEnum.SUBSCRIPTION_CREATE], owner=True),
    tags=["Abonnements"],
    summary="Souscrire à un abonnement",
    description=(
        "Crée un nouvel abonnement pour un Microtik.\n\n"
        "**Paramètres :**\n"
        "- `category_slug` : Slug de la catégorie choisie\n"
        "- `paymentMethod` : Méthode de paiement (Orange Money, etc.)\n"
        "- `phone_number` : Numéro de téléphone pour le paiement" \
        "- Admin: pour faire abonnement pour une personne." \
        "- Proprietaire: Pour faire ses abonnements"
    )
)
async def subscribe_abonement(request, data: SubscriptionWgInSchema, microtik_slug: str) -> SubscriptionResponse:
    """
    Souscrit un abonnement pour un Microtik.
    
    Args:
        request: Requête HTTP
        data (SubscriptionWgInSchema): Données de l'abonnement
        microtik_slug (str): Slug du Microtik
    
    Returns:
        SubscriptionResponse: Détails de l'abonnement et du paiement
    """
    return await subscrition_abonnement_service(
        data=data.model_dump(),
        microtik=request.microtik
    )


#------------------- LES INFORMATIONS SUR LE PAIEMENT -----------------#
@subscription.get(
    "/{microtik_slug}",
    response=list[PaidSubscriptionListSchema],
    auth=PermissionsChecker(permissions=[PermissionsEnum.SUBSCRIPTION_READ], hasWG=True),
    tags=["Abonnements"],
    summary="Lister l'historique des paiements d'abonnements d'un Microtik",
    description=(
        "Récupère la liste des paiements/abonnements associés à un Microtik.\n\n"
        "**Permissions :**\n"
        "- Admin \n"
        "- Propriétaire "
    )
)
def get_subscriptions(request, microtik_slug: str) -> list[PaidSubscriptionListSchema]:
    """
    Retourne les abonnements d'un Microtik.
    
    Args:
        microtik_slug (str): Slug du Microtik
    
    Returns:
        list[SubscriptionWgOutSchema]: Liste des paiements
    """
    
    ...


@subscription.get(
    "/details/{slug}",
    response=PaidSubscriptionDetailSchema,
    auth=PermissionsChecker(permissions=[PermissionsEnum.SUBSCRIPTION_READ]),
    tags=["Abonnements"],
    summary="Obtenir un Paiement spécifique",
    description="Récupère les détails d'un paiement par son slug la route pour les admin pour les verifications."
)
async def get_subscription(request, slug: str) -> PaidSubscriptionDetailSchema:
    """
    Retourne un abonnement spécifique.
    
    Args:
        slug (str): Slug de l'abonnement
    
    Returns:
        SubscriptionResponse: Détails de l'abonnement
    
    Raises:
        HttpError: Si l'abonnement n'existe pas
    """
    try:
        subscription = await PaidSubscription.objects.aget(slug=slug)
        return subscription
    except PaidSubscription.DoesNotExist:
        raise HttpError(
            status_code=HTTPStatus.NOT_FOUND,
            message="Abonnement non trouvé"
        )


@subscription.post("/webhook/subscription", response=WebhookOutSchemas)
def web_hook_subscription(data:WebhookSchema):
    return return_url(data=data.model_dump())


@subscription.patch(
    '/update/access/subscription/{microtik_slug}',
    response=SubscriptionWGBaseSchema,
    auth=PermissionsChecker(permissions=[PermissionsEnum.SUBSCRIPTION_UPDATE]),
    tags=['Routeurs'],
    summary="mettre a jours les informations d'access du routeur"
                    )
def update_subscription(request,microtik_slug:str,data:SubscriptionWGupdateSchema):
    data = data.model_dump()
    return update_suscription_access(
        microtik_slug=microtik_slug,
        data = data
        )


# @subscription.patch(
#     "/renew/{slug}",
#     response=SubscriptionResponse,
#     auth=PermissionsChecker(permissions=[Auth, IsOwnerMicrotik]),
#     tags=["Abonnements"],
#     summary="Renouveler un abonnement",
#     description=(
#         "Renouvelle un abonnement existant.\n\n"
#         "**Effets :**\n"
#         "- Prolonge la date d'expiration\n"
#         "- Conserve la même catégorie\n"
#         "- Génère un nouveau paiement\n\n"
#         "**Règles :**\n"
#         "- L'abonnement doit être actif ou expiré\n"
#         "- Le renouvellement se fait pour la même durée que l'abonnement initial"
#     )
# )
# async def renew_subscription(request, slug: str) -> SubscriptionResponse:
#     """
#     Renouvelle un abonnement.
    
#     Args:
#         slug (str): Slug de l'abonnement à renouveler
    
#     Returns:
#         SubscriptionResponse: Détails du renouvellement
    
#     Raises:
#         HttpError: Si l'abonnement n'existe pas
#     """
#     try:
#         subscription = await sync_to_async(SubscriptionWG.objects.get)(slug=slug)
#     except SubscriptionWG.DoesNotExist:
#         raise HttpError(
#             status_code=HTTPStatus.NOT_FOUND,
#             message="Abonnement non trouvé"
#         )
    
#     # Logique de renouvellement
#     # À implémenter selon tes besoins
    
#     return subscription