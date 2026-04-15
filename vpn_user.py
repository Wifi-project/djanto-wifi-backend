# import requests
# import urllib3
# import ipaddress

# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL = "https://localhost:5555/api/"
# ADMIN_PASS = "admin123"
# IP_DE_DEPART = "172.16.0.10"
# MASQUE = "255.255.0.0"

# def creer_utilisateur_complet(username, password, index_user):
#     ip_statique = str(ipaddress.IPv4Address(IP_DE_DEPART) + index_user)
    
#     headers = {
#         "Content-Type": "application/json",
#         "X-VPNADMIN-PASSWORD": ADMIN_PASS
#     }

#     # Payload simplifié - exactement comme dans la spécification officielle
#     payload = {
#         "jsonrpc": "2.0",
#         "id": "1",
#         "method": "CreateUser",
#         "params": {
#             "HubName_str": "DEFAULT",
#             "Name_str": username,
#             "AuthType_u32": 1,               # Authentification par mot de passe
#             "Auth_Password_str": password,    # Le serveur générera tous les hashs
#             "UsePolicy_bool": True,
#             "policy": {
#                 "IPAddress_str": ip_statique,
#                 "SubnetMask_str": MASQUE,
#                 "MaxConnection_u32": 1
#             }
#         }
#     }

#     try:
#         response = requests.post(URL, json=payload, headers=headers, verify=False)
#         result = response.json()
#         if "error" in result:
#             print(f"Erreur SoftEther : {result['error']['message']}")
#         else:
#             print(f"Succès : Utilisateur {username} créé avec l'IP {ip_statique}")
#     except Exception as e:
#         print(f"Erreur de connexion : {e}")

# # Test
# creer_utilisateur_complet("test1", "1234", 1)


import requests
import urllib3
import hashlib
import base64

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_softether_password_hash(username, password):
    # SoftEther utilise un hash spécifique : SHA0(password + username_majuscules)
    # Note: Dans beaucoup de versions d'API, un simple MD5 ou le texte clair échoue.
    # Essayons la méthode la plus compatible :
    m = hashlib.md5()
    m.update(password.encode('utf-8'))
    return base64.b64encode(m.digest()).decode('utf-8')

def creer_utilisateur_final(username, password, ip):
    url = "https://localhost:5555/api/"
    

    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "CreateUser",
        "params": {
            "HubName_str": "DEFAULT",
            "Name_str": username,
            "AuthType_u32": 1, # 1 = Password Authentication
            "Auth_Password_str": password, # On tente le clair
            # On force la policy pour l'IP
            "UsePolicy_bool": True,
            "policy": {
                "IPAddress_str": ip,
                "SubnetMask_str": "255.255.0.0"
            }
        }
    }

    headers = {"X-VPNADMIN-PASSWORD": "admin123"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, verify=False)
        data = response.json()
        
        if "error" in data:
            print(f"Erreur : {data['error']['message']}")
        else:
            print(f"Utilisateur {username} créé. Tentative de définition du mot de passe...")
            # ÉTAPE SUPPLÉMENTAIRE : On force le mot de passe après création
            set_password(username, password)
            
    except Exception as e:
        print(f"Erreur réseau : {e}")

def set_password(username, password):
    # Utilisation de SetUser pour écraser les données d'authentification
    url = "https://localhost:5555/api/"
    payload = {
        "jsonrpc": "2.0",
        "id": "2",
        "method": "SetUser",
        "params": {
            "HubName_str": "DEFAULT",
            "Name_str": username,
            "AuthType_u32": 1,
            "Auth_Password_str": password
        }
    }
    requests.post(url, json=payload, headers={"X-VPNADMIN-PASSWORD": "admin123"}, verify=False)

creer_utilisateur_final("test6", "1234", "172.16.0.26")