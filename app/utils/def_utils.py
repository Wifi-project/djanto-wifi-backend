import secrets
import string
import routeros_api


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

