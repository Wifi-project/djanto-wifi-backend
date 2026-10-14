from __future__ import annotations
from app.gdms.models import Gdms,Profil,NetworkOwner,Network,Status
from app.users.models import User
from ninja.errors import HttpError
from http import HTTPStatus
from app.utils.def_utils import  profil_duration,parse_mikrotik_rate
import secrets
from app.permissions.models import PermissionGroup
from app.gdms.utils import PermissionGroupEnum
from app.commone.email import send_mail_creation
from config import settings
# from app.gdms.tasks import provision_gdms_task
from app.gdms.api_gdms import gdms_service



#---------------------Network---------------------------------#

async def check_network_name_service(name:str) -> dict[str,str]:
    if await Network.objects.filter(name=name).aexists():
        return {"status": 'failled', "message":"Erreur ce nom de resau exist deja."}
    
    return {"status": 'success', "message":"nom de reseau valide."}


async def create_network_service(data: dict, user) -> Network:
    name = data.get('name', '')
    if not name:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="le name est obligatoir."
        )

    network_name = name.replace(" ", "_").replace("-", "_")

    if await Network.objects.filter(name=name).aexists():
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="erreur ce nom de reseau existe deja"
        )

    response = await gdms_service.create_network(network_name=network_name)

    if isinstance(response, dict):
        if response.get("status") is False:
            raise HttpError(
                status_code=HTTPStatus.BAD_GATEWAY,
                message=f"Échec routeur: {response.get('data')}",
            )
        network_id = response.get("id")
    else:
        network_id = response

    if not network_id:
        raise HttpError(
            status_code=HTTPStatus.BAD_GATEWAY,
            message=f"Identifiant réseau absent: {response}",
        )

    data.pop('id', None)
    data.pop('network_id', None)
    network = await Network.objects.acreate(**data, network_id=network_id)

    group = await PermissionGroup.objects.filter(
        slug=PermissionGroupEnum.PROPRIETAIRE_NETWORK.value
    ).afirst()

    network_owner = await NetworkOwner.objects.acreate(
        network=network,
        user=user,
    )

    if group:
        await network_owner.group_permissions.aadd(group)

    return network



def list_network_service(user:User)-> Network:
    if user.user_type == [User.OWNERSYSTEME,User.ADMIN]:
        return Network.objects.all()
    network = Network.objects.filter(owners = user)
    return network


def retrive_network_service(user:User,network_slug:str):
    return Network.objects.filter(slug=network_slug).first()


async def update_network_service(network:Network, data:dict[str,str]) -> Network:
    network_id = network.network_id
    new_name = data.get('name')

    response = await gdms_service.update_network(
        network_id=network_id,
        network_name=new_name
    )

    if not response.get('status'):
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message=f'erreur lors de la modification de network {response.get('data')}'
        )

    db_network = await Network.objects.filter(slug=network.slug).afirst()
    db_network.name = new_name
    db_network.asave(update_fields=['name'])

    return db_network


async def delete_network_service(network:Network) -> Network:
    network_id = network.network_id

    if network.gdms_network.exists():
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="erreur vous ne pouvez pas supprimer un reseau qui as des entaines."
        )

    response = await gdms_service.delete_nework(
        network_id=network_id
    )

    if response.get('status'):
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message=f'erreur de suppression du reseau {response.get('data')}'
        )

    return {"status": 'success', 'message': 'suppression effectuer avec susccess.'}



#--------------------- Gdms ---------------------------#

async def create_gdms_service(data:dict[str,str|int], user:User, network:Network) -> Gdms:    
    network_id = network.network_id
    ssid_name = network.name
    mac = data.get("mac",'')
    password = data.get("password","")

    if not mac or not password:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="le mac et le passwork son obligatoire"
        )

    if await Gdms.objects.filter(mac_address=mac, password=password).aexists():
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="erreur cet entaine a deja ete ajouter."
        )

    gdms = await Gdms.objects.filter(network=network,mac_address = mac).afirst()
    if not gdms:
        r_app_device = await gdms_service.device_add_ap(
            network_id=network_id,
            mac=mac,
            password=password,
            name=ssid_name
        )


        print('--------response app_device',r_app_device)
    
        status_r_app_device = r_app_device.get("status")
        if not status_r_app_device:
            raise HttpError(
                status_code=HTTPStatus.BAD_REQUEST,
                message=f"une erreur lors de la creation de network : {r_app_device.get('data')}"
                )
    
        gdms = await Gdms.objects.acreate(**data, network=network,device_add=True)

    ssid = await gdms_service.create_ssid(
        network_id=network_id,
        ssid_name=ssid_name
    )

    print('---------les donnees', ssid)

    if not ssid.get('status'):
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message=f'erreur de la creation ssid {ssid.get('data')}'
        )

    data = ssid.get('data')
    gdms.gdms_site_id = data.get('id')
    await gdms.asave(update_fields=['gdms_site_id'])

    return gdms


async def reboot_device_service(network:Network, data:dict[str,list[str]]) -> dict[str,str]:
    network_id = network.network_id
    mac = data.get('mac')

    response = await gdms_service.device_reboot_aps(
        network_id=network_id,
        mac_list=list(mac)
    )

    if not response.get('status'):
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message=f'erreur de redemarrage {response.get('data')}'
        )

    return {'status':'success', 'message': 'redemarrer avec success.'}


async def delete_device_service(data:dict[str,list[str]]) -> dict[str,str]:
    mac = data.get('mac')

    response = await gdms_service.device_delete(
        mac_list=mac
    )

    if not response.get('status'):
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message=f'erreur de suppresssion {response.get('data')}'
        )

    return {'status': 'success', 'message': 'suppression effectuer avec success.'}


async def ssid_update_service(network:Network, gdms_slug:str, new_name:str) -> Gdms:
    network_id = network.network_id
    name = network.name

    gdms = await Gdms.objects.filter(slug=gdms_slug).afirst()
    ssid_id = gdms.gdms_site_id

    response = await gdms_service.update_ssid(
        network_id=network_id,
        ssid_id=ssid_id,
        new_name=new_name,
        current_ssid_name=name
    )

    if not response.get('status'):
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message=f"erreur lors de la mise a jours {response.get('data')}"
        )
    
    return gdms


async def block_ssid_service(network:Network, gdms_slug:str) -> Gdms:
    network_id = network.network_id
    name = network.name

    gdms = await Gdms.objects.filter(slug=gdms_slug).afirst()
    ssid_id = gdms.gdms_site_id

    response = await gdms_service.block_unblock_ssid(
        network_id=network_id,
        ssid_id=ssid_id,
        current_ssid_name=name,
        block=True
    )

    if not response.get('status'):
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message=f"erreur lors du blocage ssid {response.get('data')}"
        )
    gdms.status = Status.DISABLE
    await gdms.asave(update_fields=['status'])

    return {'status': 'success', 'message':'le blocage effectuer avec success.'}


async def unblock_ssid_service(network:Network, gdms_slug:str) -> Gdms:
    network_id = network.network_id
    name = network.name

    gdms = await Gdms.objects.filter(slug=gdms_slug).afirst()
    ssid_id = gdms.gdms_site_id

    response = await gdms_service.block_unblock_ssid(
        network_id=network_id,
        ssid_id=ssid_id,
        current_ssid_name=name,
        block=False
    )

    if not response.get('status'):
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message=f"erreur lors du deblocage ssid {response.get('data')}"
        )
    gdms.status = Status.DISABLE
    await gdms.asave(update_fields=['status'])

    return {'status': 'success', 'message':'le deblocage effectuer avec success.'}


async def isolation_ssid_service(network:Network, gdms_slug:str) -> Gdms:
    network_id = network.network_id
    name = network.name

    gdms = await Gdms.objects.filter(slug=gdms_slug).afirst()
    ssid_id = gdms.gdms_site_id

    response = await gdms_service.set_client_isolation(
        network_id=network_id,
        ssid_id=ssid_id,
        current_ssid_name=name,
        block=True
    )

    if not response.get('status'):
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message=f"erreur lors du deblocage ssid {response.get('data')}"
        )
    gdms.set_isloation = True
    await gdms.asave(update_fields=['status'])

    return {'status': 'success', 'message':'isolation effectuer avec success.'}



#----------------------OWNER MICROTIK----------------------------------

def create_owner_service(network:Network,owner_data:dict) -> NetworkOwner:
    email = owner_data.get("email", "")
    if User.objects.filter(email=email).exists():
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message={'Ce address email exist est deja attribuer à un user.'}
            )
    pwd = secrets.token_urlsafe(8)
    user = User.objects.create_user(**owner_data,user_type=User.OWNERMICROTIK, password=pwd)
    group = PermissionGroup.objects.filter(slug = PermissionGroupEnum.GERANT_MICROTIK.value).first()
    # permis = set(perm for perm in group.permissions.all())

    network_owner = NetworkOwner.objects.create(
        network=network,
        user = user
    )
    # network_owner.permissions.add(*permis)
    network_owner.group_permissions.add(group)
    username = f"{user.first_name} {user.last_name} "
    send_mail_creation(username=username, email=user.email,pwd=pwd)

    return network_owner



def add_owner_service(network:NetworkOwner, email:str) -> NetworkOwner:
    user = User.objects.filter(email=email).first()
    if not user:
        raise HttpError(status_code=HTTPStatus.BAD_REQUEST,
                        message="aucun utilisateur associer à ce mail."
                        )

    if NetworkOwner.objects.filter(network=network, user=user).exists():
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Cet utilisateur figure deja parmis les gerant de ce reseau."
        )
    
    network_owner = NetworkOwner.objects.create(
        network=network,
        user=user
    )

    group = PermissionGroup.objects.filter(slug = PermissionGroupEnum.GERANT_MICROTIK.value).first()
    # permis = set(perm for perm in group.permissions.all())

    # network_owner.permissions.add(*permis)
    network_owner.group_permissions.add(group)

    return network_owner



def remove_owner_service(network:Network, user_slug:str) -> dict:
    user = User.objects.filter(slug=user_slug).first()
    if not user:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Aucun utilisateur associer à ce slug."
        )
    NetworkOwner.objects.filter(
        network=network,
        user=user
    ).first().delete()

    return {"status":"success","message":"La suppression effectuer avec success."}

#--------aucune utiliter pour le moment-----------------#
def add_owner_group_service(network:Network, slug_user:str, slug_group:str) -> NetworkOwner:
    user = User.objects.filter(slug=slug_user).first()
    if not user:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message='Aucun utilisateur attribuer a ce slug.'
        )

    group = PermissionGroup.objects.filter(slug=slug_group).first()
    if not group:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message='Aucun groupe de permissions trouvé avec ce slug.'
        )
    
    permissions = group.permissions.all()

    microtik_owner = NetworkOwner.objects.filter(
        network=network,
        user=user
    ).first()

    microtik_owner.permissions.add(*permissions)
    return {"status":"success", "message":"Utilisateur ajouter dans le group avec success."}



def remove_owner_group_service(network:Network, slug:str, slug_group:str) -> NetworkOwner:
    """Retirer les permission d'un gestionnaire"""

    user = User.objects.filter(slug=slug).first()
    if not user:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message='Aucun utilisateur attribuer a ce slug.'
        )

    group = PermissionGroup.objects.filter(slug=slug_group).first()
    if not group:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message='Aucun groupe de permissions trouvé avec ce slug.'
        )
    
    slug_permissions = group.permissions.values_list('slug')

    microtik_owner = NetworkOwner.objects.filter(
        network=network,
        user=user
    ).first()

    resist_perms = microtik_owner.permissions.exclude(slug__in=slug_permissions)
    microtik_owner.permissions.set(*resist_perms)
    return {"status":"success", "message":"Utilisateur ajouter dans le group avec success."}



#-------------- Profil ------------------------#

def create_profil_service(data: dict, network: Network) -> Profil:

    type_session = data.pop('type_session', 'h')
    duration = data.pop('duration', 1)
    session_timeout,session_timeout_dict = profil_duration(duration=duration, type_session=type_session)
    price = data.get("price", 0.00)
    
    profile_name = data.get("name", "default_profil")
    rate_limit = data.get("rate_limit", "512k/1M")
    shared_users = str(data.get("shared_users", 1))
    up_rate, down_rate = parse_mikrotik_rate(rate_limit)

    return Profil.objects.create(
        name=profile_name,
        rate_limit=rate_limit,
        shared_users=int(shared_users),
        session_timeout=session_timeout,
        session_timeout_dict = session_timeout_dict,
        price=price,
        network=network,
        up_rate= up_rate,
        down_rate = down_rate
    )
        


def update_profil_service(network: Network, slug_profil: str, data: dict) -> Profil:

    profil = network.profils.filter(slug=slug_profil).first()
    if not profil: 
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Aucun profil correspondant à ce slug."
        )
    
    type_session = data.pop('type_session', '')
    duration = data.pop('duration', '')
    
    session_timeout,session_timeout_dict = None,None
    if type_session and duration:
        session_timeout,session_timeout_dict = profil_duration(duration=duration, type_session=type_session)
        data['session_timeout'] = session_timeout
        data['session_timeout_dict'] = session_timeout_dict
        
    rate_limit = data.get('rate_limit','')
    if rate_limit:
        up_rate, down_rate = parse_mikrotik_rate(rate_limit)
        data['up_rate'] = up_rate
        data['down_rate'] = down_rate

    for key, value in data.items():
        if hasattr(profil, key):  
            setattr(profil, key, value)
    profil.save()

    return profil


def delete_profil_service(network: Network, profil_slug: str) -> dict:
    profil = network.profils.filter(slug=profil_slug).first()
    if not profil: 
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Aucun profil correspondant à ce slug."
        )
    
    profil.is_active = False
    profil.save(update_fields=['is_active'])
        
    return {"status": "success", "message": "Profil supprimé avec succès."}
        


def profil_liste_service(microtik_slug:str):
    microtik = Network.objects.filter(slug=microtik_slug).first()
    
    profil = microtik.profils.all()

    return profil



