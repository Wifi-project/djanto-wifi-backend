from ninja.errors import HttpError
from app.users.models import User
from app.finances.models import GainSysteme, Windraw, Status
from app.gdms.models import Network
from django.contrib.auth.hashers import check_password
from app.finances.utils import calcul_deduction
from app.api_extern.adapterPayement import AdapterPayement


def info_deposit_list(microtik:str):
    return InfoDeposit.objects.filter(microtik=microtik)


def info_deposit_retrive(microtik:Microtik,deposit_slug:str):
    info_depot = InfoDeposit.objects.filter(
        slug = deposit_slug,
        microtik=microtik,
        ).first()

    if not info_depot:
        raise HttpError(
            status_code=404,
            message="Aucun client avec ce slug trouver."
        )
    return info_depot




def windraw_service(network:Microtik,data:dict, user:User):
    amount = data.get('amount',0)
    # phone_number = data.get("phone_number","")
    password = data.get("password","")
    provider = data.get("provider",'OM')


    if not password:
        raise HttpError(
            status_code=404,
            message="Veillez saisir voitre mot de passe pour initier le retrait."
        )
    
    if not check_password(password=password, encoded=user.password):
        raise HttpError(
            status_code=404,
            message="Le mot de passe saisie est incorect.\n Il vous rest 2 tentative"
        )

    if amount < 10000:
        raise HttpError(
            status_code=400,
            message="Le montant minimum pour le retrait est de 10 000 GNF"
        )
    
    availble_windraw = network.amount_available_windrawal
    if availble_windraw < amount :
        raise HttpError(
            status_code=404,
            message="Le motant saisie est superieur au montant disponible pour le retrait."
        )

    amout_windraw,gain = calcul_deduction(amount,network.commission_rate)

    adapter = AdapterPayement(code="djomy")
    
    Windraw.objects.create(
        network=network,
        amount = amout_windraw,
        phone_number = user.phone_number,
        user = user,
    )

    djomy = adapter.payOut(
        message="Paiement des ",
        amount=amount,
        beneficiary_name=user.get_username,
        number=user.phone_number,
        provider=provider
    )


    #send mail for approve this windraw

    return {'status': "success", "message":"Votre retrait a été initier avec success.\n"
    "veillez patientez pendant la verification et la validation."}




def historique_windraw_service(
        microtik:Microtik,
        status:str | None = None,
        reference: str | None = None
        ):
    
    historiques = (
        Windraw.objects
        .filter(microtik=microtik)
        .select_related("microtik")
        .order_by("-update_at"))
    
    if status:
        historiques = historiques.filter(status=status)

    if reference:
        historiques = historiques.filter(reference=reference)
    

    return historiques


def windraw_retrieve_service(slug,microtik:Microtik):
    try:
        return Windraw.objects.filter(
            microtik=microtik,
            slug=slug
        )

    except Windraw.DoesNotExist:
        raise HttpError(
            status_code=404,
            message="Le slug entrez est incorect."
        )


def cancel_windraw_service(microtik, slug):
    try:
        windraw = Windraw.objects.filter(
            microtik=microtik,
            slug=slug
        )

    except Windraw.DoesNotExist:
        raise HttpError(
            status_code=404,
            message="Le slug entrez est incorect."
        )
    
    if windraw.status != Status.PENDING:
        raise HttpError(
            status_code=404,
            message="Erreur cette demande ne  plus etre annuler."
        )
    
    windraw.status = Status.CANCELLED
    windraw.save()

    return {"status": "success", "message":"La demande a été annuler avec success."}
