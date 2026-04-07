from ninja import Router
from ninja.errors import HttpError
from http import HTTPStatus
from app.users.models import User
from ninja.pagination import paginate,LimitOffsetPagination
from app.users.deps import GlobalAuth
from typing import List
from app.microtiks.models import Microtik,Profil
from app.microtiks.services import (
    create_microtik_service,
    update_microtik_service,
    check_connexion as check_connexion_service,
    create_profil_service,
    update_profil_service,
    delete_profil_service as delete,
    profil_liste_service,
    retrieve_microtik_service
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
    return create_microtik_service(data=data.model_dump(), user=user)


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
    return update_microtik_service(
        data=data.model_dump(exclude_unset=True), 
        user = user,
        slug=slug)


@microtik_router.get(
        "/list/", 
        response=list[MicrotikOutListSchemas], 
        description="afficher la liste des microtiks appartenant a la personne connecter," \
        "si la personne connecter est un admin il verra la liste de tous les microtiks existant.",
        auth=GlobalAuth()
        )
@paginate(LimitOffsetPagination, papage_size=10)
def list_microtik(request):
    user = request.user
    if user.user_type == User.OWNERSYSTEME or User.ADMIN:
        microtik = Microtik.objects.all()
    else:
        microtik = Microtik.objects.filter(owner=user)
    return microtik


@microtik_router.get(
        "/retrieve/{microtik_slug}/", 
        response=MicrotikOutRetrieveSchemas,
        auth=GlobalAuth([]),
        description="afficher les details d'un microtik."
        )
def retrieve_microtik(request,microtik_slug:str) -> MicrotikOutRetrieveSchemas:
    user = request.user
    return retrieve_microtik_service(
        microtik_slug=microtik_slug,
        user=user
    )



#------------------------------LES PROFILES -------------------------------#

@microtik_router.post(
        '/{microtik_slug}/profile-create/', 
        response=MicrotikCheckResponseSchemas, 
        description="creation des profil pour un microtik"
        )
def profile_create(request,data:ProfilInSchema, microtik_slug:str) -> MicrotikCheckResponseSchemas:
    user = request.user
    return create_profil_service(
        data=data.model_dump(),
        microtik_slug=microtik_slug,
        user = user
        )


@microtik_router.patch(
        '/{microtik_slug}/update-profile/{slug_profil}/', 
        response=MicrotikCheckResponseSchemas,
        description="La mise a jour du profile microtik"
        )
def profile_update(request,data:ProfilUpdateSchema,microtik_slug:str,slug_profil:str) -> MicrotikCheckResponseSchemas:
    user = request.user 

    return update_profil_service(
        microtik_slug=microtik_slug,
        slug_profil=slug_profil, 
        user = user,
        data=data.model_dump(exclude_unset=True)
        )


@microtik_router.delete(
        '/{microtik_slug}/delete-profil/{slug_profil}/',
        response=MicrotikCheckResponseSchemas,
        description="Supprimer un profil"
        )
def delete_profil(request,microtik_slug:str,slug_profil:str) -> MicrotikCheckResponseSchemas:
    user = request.user 

    return delete(
        microtik_slug=microtik_slug,
        profil_slug=slug_profil,
        user = user
    )


@microtik_router.get(
        '/{microtik_slug}/list-profil/', 
        response= List[ProfilOutSchema],
        description="Afficher la liste des proles d'un microtik.",
        auth=None
        )
def list_profil(request,microtik_slug:str):
    # user = request.user 
    return profil_liste_service(
        microtik_slug=microtik_slug
        )