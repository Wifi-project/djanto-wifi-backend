from ninja import Router
from ninja.errors import HttpError
from http import HTTPStatus
from app.users.models import User
from ninja.pagination import paginate,LimitOffsetPagination
from app.users.deps import GlobalAuth
from app.microtiks.models import Microtik,Profil
from app.microtiks.services import (
    create_microtik,
    update_microtik,
    check_connexion as check_connexion_service,
    create_profil,
    update_profil,
    delete_profil as delete,
    profil_liste
)
from app.microtiks.schemas import (
    MicrotikInSchemas,
    MicrotikOutListSchemas,
    MicrotikOutRetrieveSchemas,
    MicrotikUpdateSchemas,
    MicrotikCheckSchemas,
    MicrotikCheckResponseSchemas,
    ProfilInSchema,
    ProfilOutSchema,
    ProfilUpdateSchema
)
from ninja_simple_jwt.auth.ninja_auth import HttpJwtAuth


microtik_router = Router(tags=["Microtik"], auth=[GlobalAuth()])


#--------------------------GESTION MICROTIK----------------------#
@microtik_router.post(
        "/create",
        response=MicrotikOutListSchemas,
        description="La creation d'un microtik",
        )
def create(request,data:MicrotikInSchemas):
    user = request.user 
    return create_microtik(data=data.model_dump(), user=user)


@microtik_router.post(
        "/check-connexion", 
        response=MicrotikCheckResponseSchemas, 
        description="Verifier la connexion avec le microtik voir si les infos saisies sont exactent"
        )
def check_connexion(request,data:MicrotikCheckSchemas) -> MicrotikCheckResponseSchemas:
    return check_connexion_service(data=data.model_dump())

@microtik_router.patch(
    "/update/{slug}", 
    response=MicrotikOutListSchemas,
    description="Modifier un microtik",
    auth=[GlobalAuth()]  
)
def update(request, data: MicrotikUpdateSchemas, slug: str) -> MicrotikOutListSchemas:
    user = request.user

    if not user.microtiks.filter(slug=slug).exists():
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Ce microtik ne t'appartient pas."
        )
    
    return update_microtik(data=data.model_dump(exclude_unset=True), slug=slug)


@microtik_router.get(
        "/list/", 
        response=list[MicrotikOutListSchemas], 
        description="afficher la liste des microtik",
        auth=GlobalAuth()
        )
@paginate(LimitOffsetPagination, papage_size=10)
def list_microtik(request):
    user = request.user
    return Microtik.objects.filter(owner=user)


@microtik_router.get(
        "/retrieve/{slug}/", 
        response=MicrotikOutRetrieveSchemas,
        description="afficher les details d'un microtik."
        )
def retrieve_microtik(request,slug:str) -> MicrotikOutRetrieveSchemas:
    try:
        microtik = Microtik.objects.get(slug=slug)
        return microtik
    except Microtik.DoesNotExist:
        return HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Aucun microtik trouver existant avec ce slug."
        )


#------------------------------LES PROFILES -------------------------------#

@microtik_router.post(
        '/{slug_microtik}/profile-create/', 
        response=MicrotikCheckResponseSchemas, 
        description="creation des profil pour un microtik"
        )
def profile_create(request,data:ProfilInSchema, slug_microtik:str) -> MicrotikCheckResponseSchemas:
    return create_profil(data=data.model_dump(), slug_microtik=slug_microtik)


@microtik_router.patch(
        '/{slug_microtik}/update-profile/{slug_profil}/', 
        response=MicrotikCheckResponseSchemas,
        description="La mise a jour du profile microtik"
        )
def profile_update(request,data:ProfilUpdateSchema,slug_microtik:str,slug_profil:str) -> MicrotikCheckResponseSchemas:
    return update_profil(
        slug_microtik=slug_microtik,
        slug_profil=slug_profil, 
        data=data.model_dump(exclude_unset=True)
        )


@microtik_router.delete(
        '/{slug_microtik}/delete-profil/{slug_profil}/',
        response=MicrotikCheckResponseSchemas,
        description="Supprimer un profil"
        )
def delete_profil(request,slug_microtik:str,slug_profil:str) -> MicrotikCheckResponseSchemas:
    return delete(
        microtik_slug=slug_microtik,
        profil_slug=slug_profil
    )


@microtik_router.get(
        '/{slug_microtik}/list-profil/', 
        response= list[ProfilOutSchema],
        description="Afficher la liste des proles d'un microtik."
        )
def list_profil(request,slug_microtik:str):
    return profil_liste(microtik_slug=slug_microtik)