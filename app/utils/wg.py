import httpx
import os 

WGEASY_API_BASE_URL = os.getenv('WGEASY_API_URL', "http://localhost:51821").rstrip("/api")
WGEASY_PASSWORD = os.getenv("WGEASY_PASSWORD", "admin123")


def create_wg_user(name: str):
    """
    Crée un nouvel utilisateur (client) sur wg-easy et retourne ses informations.
    """

    response = httpx.post(
        f"{WGEASY_API_BASE_URL}/api/wireguard/client",
        json={"name": name},
        auth=httpx.BasicAuth("", WGEASY_PASSWORD), 
        timeout=10.0
    )
    response.raise_for_status()
    return {
        "status": "success",
        "message": f"Utilisateur {name} créé avec succès.",
        "data": response.json()
    }



def disable_expired_subscriptions(id_wg:str):
    
    response = httpx.post(
        f"{WGEASY_API_BASE_URL}/api/wireguard/client/{id_wg}/disable",
        auth=httpx.BasicAuth("", WGEASY_PASSWORD),
        timeout=5.0
    )
    response.raise_for_status()
    return {'status': 'success', 'message': "bloquer avec success."}
