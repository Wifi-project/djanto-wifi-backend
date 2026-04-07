from ninja.errors import HttpError
from app.clients.models import InfoDeposit
from app.users.models import User
from app.finances.models import GainSysteme, Windraw
from app.microtiks.models import Microtik


def info_deposit_list(microtik_slug:str,owner:User):
    return InfoDeposit.objects.filter(microtik__slug=microtik_slug)


def info_deposit_retrive(microtik_slug:str,deposit_slug:str,owner:User):
    info_depot = InfoDeposit.objects.filter(
        slug = deposit_slug,
        microtik__slug=microtik_slug,
        ).first()

    if not info_depot:
        raise HttpError(
            status_code=404,
            message="Aucun client avec ce slug trouver."
        )
    return info_depot


def windraw_service(microtik_slug:str,data:dict, user:User):
    amount = data.get('amoun',0)
    phone_number = data.get("phone_number","")
    microtik = Microtik.objects.filter(slug=microtik_slug).first()

    availble_windraw = microtik.get_amount_available_windrawal
    if availble_windraw < amount :
        raise HttpError(
            status_code=404,
            message="Le motant saisie est superieur au montant disponible pour le retrait."
        )
    
    windraw = Windraw.objects.create(
        microtik=microtik,
        amount = amount,
        phone_number = phone_number,
        user = user,
    )

    #appel api 




def historique_windraw_service(
        user:User,
        microtik_slug:str | None = None,
        status:str | None = None
        ):
    historiques = Windraw.objects.order_by("-update_at")
    if status:
        historiques = historiques.filter(status=status)
    
    if microtik_slug:
        historiques = historiques.filter(microtik__slug = microtik_slug)

    return historiques


