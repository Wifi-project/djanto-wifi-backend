import secrets
import string
from app.gdms.schemas import ProfilDuratinEnum
from app.users.models import User
import re

def generer_code_unique(longueur=8):
    character = (
            string.ascii_letters +
            string.digits
    )

    return ''.join(secrets.choice(character) for _ in range(longueur))



def profil_duration(duration: int, type_session: ProfilDuratinEnum) -> str:
    if type_session == ProfilDuratinEnum.MINUTES:
        return f"00:{duration:02d}:00",{'d':0,'h':0,'m':int(duration)}
    elif type_session == ProfilDuratinEnum.HOURS:
        return f"{duration:02d}:00:00", {'d':0,'h':int(duration),'m':0}
    elif type_session == ProfilDuratinEnum.DAYS:
        return f"{duration}d 00:00:00", {'d':int(duration),'h':0,'m':0}
    return "00:00:00",{'d':0,'h':0,'m':0}




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