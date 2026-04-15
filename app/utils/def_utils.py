import secrets
import string
import routeros_api
from app.microtiks.schemas import ProfilDuratinEnum
from app.users.models import User
from app.microtiks.models import Microtik
from ninja.errors import HttpError

def generer_code_unique(longueur=8):
    character = (
            string.ascii_letters +
            string.digits
    )

    return ''.join(secrets.choice(character) for _ in range(longueur))


def connect_microtik(ip,username,password):

    connection = routeros_api.RouterOsApiPool(
        ip, 
        username=username, 
        password=password,
        port=8728,
        use_ssl=False,
        plaintext_login=True
        )
    try:
        # api = connection.get_api()
        return connection
    except Exception as e:
        return {"status":False, "message":f"Erreur de connexion. \n *** {e}"}
    finally:
        try: connection.disconnect()
        except: pass



def profil_duration(duration,type_session):
    if type_session == ProfilDuratinEnum.MINUTES:
        session_timeout = f"00:{duration:02d}:00"
    elif type_session == ProfilDuratinEnum.HOURS:
        session_timeout = f"{duration:02d}:00:00"
    elif type_session == ProfilDuratinEnum.DAYS:
        session_timeout = f"{duration}d 00:00:00"
    return session_timeout


def creer_ticket_code(
        microtik:Microtik,
        code_paye:list, 
        profile_name:str, 
        limit_uptime:str, 
        comment:str) -> dict:

    vpn = microtik.suscription_vpn

    connection = connect_microtik(
        ip=vpn.vpn_ip,
        username=vpn.vpn_username,
        password=vpn.vpn_password
        )

    api = connection.get_api()
    list_user = api.get_resource('/ip/hotspot/user')
    
    try:
        for code in code_paye:
            list_user.add(
                name=code, 
                password=code, 
                profile=profile_name,
                limit_uptime = limit_uptime,
                comment=comment
            )
        return {"status":"success","message":f"success"}
    
    except Exception as e:
        if "already exists" in str(e).lower():
            pass

        return {"status":"failled","message":f"Erreur MikroTik : {e}"}
    
    finally:
        connection.disconnect()



