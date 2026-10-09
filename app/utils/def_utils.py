import secrets
import string
import routeros_api
from app.microtiks.schemas import ProfilDuratinEnum
from app.users.models import User
from app.microtiks.models import Microtik
from ninja.errors import HttpError
import re

def generer_code_unique(longueur=8):
    character = (
            string.ascii_letters +
            string.digits
    )

    return ''.join(secrets.choice(character) for _ in range(longueur))


def connect_microtik(ip, username, password):
    """
    Initialise et teste la connexion au MikroTik via l'IP WireGuard.
    Retourne l'objet connection utilisable si réussi, ou un dictionnaire d'erreur.
    """
    connection = routeros_api.RouterOsApiPool(
        host=ip, 
        username=username, 
        password=password,
        port=8728,
        plaintext_login=True
    )
    try:
        api = connection.get_api() 
        return {"status": True, "pool": connection, "api": api}
    except Exception as e:
        try: connection.disconnect()
        except: pass
        return {"status": False, "message": f"Erreur de connexion VPN/API. \n *** {e}"}



def profil_duration(duration: int, type_session: ProfilDuratinEnum) -> str:
    if type_session == ProfilDuratinEnum.MINUTES:
        return f"00:{duration:02d}:00",{'d':0,'h':0,'m':int(duration)}
    elif type_session == ProfilDuratinEnum.HOURS:
        return f"{duration:02d}:00:00", {'d':0,'h':int(duration),'m':0}
    elif type_session == ProfilDuratinEnum.DAYS:
        return f"{duration}d 00:00:00", {'d':int(duration),'h':0,'m':0}
    return "00:00:00",{'d':0,'h':0,'m':0}



def creer_ticket_code(
        microtik:Microtik,
        code_paye:list, 
        profile_name:str, 
        limit_uptime:str, 
        comment:str) -> dict:

    wg = microtik.subscriptionwg

    res_conn = connect_microtik(
        ip=wg.wg_ip,  
        username=wg.mikrotik_username,
        password=wg.mikrotik_password  
    )

    if not res_conn["status"]:
        return {"status": "failed", "message": res_conn["message"]}

    pool = res_conn["pool"]
    api = res_conn["api"]
    list_user = api.get_resource('/ip/hotspot/user')
    
    codes_crees = 0
    codes_existants = 0
    code_created = []

    try:
        for code in code_paye:
            try:
                list_user.add(
                    name=code, 
                    password=code, 
                    profile=profile_name,
                    limit_uptime=limit_uptime,
                    comment=comment
                )
                codes_crees += 1
                code_created.append(code)

            except Exception as e:
                if "already exists" in str(e).lower():
                    codes_existants += 1
                    continue
                else:
                    raise e

        return {
            "status": "success",
            "message": f"{codes_crees} ticket(s) créé(s) avec succès. ({codes_existants} déjà existant(s))",
            "codes": code_created
        }
    
    except Exception as e:
        return {"status": "failed", "message": f"Erreur MikroTik critique durant la génération : {e}"}
    
    finally:
        pool.disconnect()



def parse_mikrotik_rate(rate_limit: str) -> tuple[int, int]:
    """
    Parse '512k/1M' → (512, 1024) en Kbps.
    Gère k, K, m, M, g, G et l'absence d'unité.
    """
    if "/" not in rate_limit:
        raise ValueError(f"Format invalide : {rate_limit!r}")

    up_str, down_str = rate_limit.split("/", 1)
    pattern = re.compile(r"^(\d+)([kKmMgG]?)$")
    multipliers = {"": 1, "k": 1, "m": 1024, "g": 1024 * 1024}

    def to_kbps(value: str) -> int:
        match = pattern.match(value.strip())
        if not match:
            raise ValueError(f"Valeur invalide : {value!r}")
        number, unit = match.groups()
        return int(number) * multipliers[unit.lower()]

    return to_kbps(up_str), to_kbps(down_str)