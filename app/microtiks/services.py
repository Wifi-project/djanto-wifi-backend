from app.microtiks.models import Microtik,Profil
from app.users.models import User
from ninja.errors import HttpError
from http import HTTPStatus
from app.microtiks.schemas import ProfilDuratinEnum
from app.utils.def_utils import connect_microtik, profil_duration, check_property_microtik


def create_microtik_service(data:dict[str,str|int], user:User) -> Microtik:
    return Microtik.objects.create(**data,owner=user)


def update_microtik_service(slug:str,data:dict[str,str|int], user:User) -> Microtik:
    microtik = check_property_microtik(
        microtik_slug=slug,
        user=user
    )

    for key,value in data.items():
        setattr(microtik, key,value)
    microtik.save()
    
    return microtik


def retrieve_microtik_service(microtik_slug, user):

    return check_property_microtik(
        microtik_slug=microtik_slug,
        user=user
    )


def check_connexion(data:dict):
    ip = data.get("ip","")
    username = data.get("username","")
    password = data.get("password","")
    if not ip or not username or not password:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Vous devez renseigner le ip, username, password obligatoirement"
        )
    connection = connect_microtik(ip=ip,username=username,password=password)
    try:
        api = connection.get_api()
        return {"status":True, "message":"Connexion etablie avec success."}
    except Exception as e:
        return {"status":False, "message":f"Erreur de connexion. \n *** {e}"}
    finally:
        try: connection.disconnect()
        except: pass


def create_profil_service(data:dict, microtik_slug:str, user:User) -> Profil:
    microtik = check_property_microtik(
        microtik_slug=microtik_slug,
        user=user
    )

    if not microtik:
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Aucun microtik n'exist avec ce slug."
        )
    
    type_session = data.pop('type_session')
    duration = data.pop('duration',1)

    session_timeout = profil_duration(duration=duration, type_session=type_session)
    connection = connect_microtik(
        ip=microtik.ip,
        username=microtik.username,
        password=microtik.password
        )
    
    api = connection.get_api()
    profiles = api.get_resource('/ip/hotspot/user/profile')
    try:
        profiles.add(
            name=data.get("name","default_profil"),
            rate_limit=data.get("rate_limit","512k/1M"),
            shared_users=str(data.get("shared_users",1)),
            session_timeout= session_timeout
        )
        Profil.objects.create(**data, 
                                microtik=microtik, 
                                session_timeout=session_timeout
                                )
        return {"status":True, "message":"profile cree avec success"}
    except Exception as e:
        return {"status":False, "message":"la creation du profil echouer"}
    finally:
        connection.disconnect()



def update_profil_service(microtik_slug:str,user:User,slug_profil:str, data:dict) -> Profil:
    microtik = check_property_microtik(
        microtik_slug=microtik_slug,
        user=user
    )
    
    profil = microtik.profils.filter(slug=slug_profil).first()
    if not profil: 
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Aucun profil correspondant a ce slug."
        )
    
    type_session = data.pop('type_session', "")
    duration = data.pop('duration',0)
    
    session_timeout = None
    if type_session and duration:
        session_timeout = profil_duration(duration=duration, type_session=type_session)

    connection = connect_microtik(
        ip=microtik.ip,
        username=microtik.username,
        password=microtik.password
        )
    api = connection.get_api()
    profiles = api.get_resource('/ip/hotspot/user/profile')

    all_profiles = profiles.get()

    profil_existant = None
    for p in all_profiles:
        if p.get('name') == profil.name:  # profil.name est le nom existant
            profil_existant = p
            break

    if profil_existant:
        try:
            profiles.set(
                id=profil_existant['id'], 
                name=data.get("name", profil.name),
                rate_limit=data.get("rate_limit", profil.rate_limit),
                shared_users=str(data.get("shared_users", profil.shared_users)),
                session_timeout=session_timeout if session_timeout else profil.session_timeout
            )

            for key,value in data.items():
                setattr(profil, key,value)
            profil.save()

            return {"status": True, "message": "profile modifie avec success"}
        except Exception as e:
            return {"status": False, "message": f"la modification du profil a echoue {e}"}
        finally:
            connection.disconnect()



def delete_profil_service(microtik_slug:str,profil_slug:str, user:User):
    microtik = check_property_microtik(
        microtik_slug=microtik_slug,
        user=user 
    )
    
    profil = microtik.profils.filter(slug=profil_slug).first()
    if not profil: 
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Aucun profil correspondant a ce slug."
        )
    
    connection = connect_microtik(
        ip=microtik.ip,
        username=microtik.username,
        password=microtik.password
        )
    
    api = connection.get_api()
    profiles = api.get_resource('/ip/hotspot/user/profile')
    try:
        profiles.remove(name=profil.name)
        profil.delete()
        return {"status": True, "message": "profile supprime avec success"}
    except Exception as e:
        return {"status": False, "message": "la suppression du profil a echoue"}
    finally:
        connection.disconnect()


def profil_liste_service(microtik_slug:str):
    microtik = Microtik.objects.filter(slug=microtik_slug).first()
    
    profil = microtik.profils.all()

    return profil







