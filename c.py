import requests
import urllib3
import ipaddress


# /interface l2tp-client
# add name=vpn-softether 
# connect-to=IP_DE_VOTRE_SERVEUR user="mikrotik_client_1" password="pass123" disabled=no


# /ip service enable api

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION ---
URL = "https://localhost:5555/api/"
ADMIN_PASS = "votre_mot_de_passe_admin"
IP_STORAGE_FILE = "last_ip.txt"
START_IP = "192.168.30.50" # Première IP à distribuer

def get_next_ip():
    try:
        # Lire la dernière IP utilisée
        with open(IP_STORAGE_FILE, "r") as f:
            last_ip = f.read().strip()
            next_ip = str(ipaddress.IPv4Address(last_ip) + 1)
    except FileNotFoundError:
        # Si le fichier n'existe pas, on commence à START_IP
        next_ip = START_IP
    
    # Sauvegarder la nouvelle IP pour la prochaine fois
    with open(IP_STORAGE_FILE, "w") as f:
        f.write(next_ip)
    return next_ip

def create_auto_user(username, password):
    statique_ip = get_next_ip()
    
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "CreateUser",
        "params": {
            "HubName_str": "DEFAULT",
            "Name_str": username,
            "AuthType_u32": 1,
            "Auth_Password_str": password,
            "UsePolicy_bool": True,
            "policy": {
                "IPAddress_str": statique_ip,
                "SubnetMask_str": "255.255.255.0"
            }
        }
    }

    headers = {
        "Content-Type": "application/json",
        "X-VPNADMIN-PASSWORD": ADMIN_PASS
    }

    try:
        response = requests.post(URL, json=payload, headers=headers, verify=False)
        res_data = response.json()
        if "error" in res_data:
            print(f"Erreur : {res_data['error']['message']}")
        else:
            print(f"Utilisateur {username} créé avec l'IP : {statique_ip}")
    except Exception as e:
        print(f"Erreur réseau : {e}")

# Exemple d'utilisation
create_auto_user("client_01", "pass123")
create_auto_user("client_02", "pass456")