import requests
import urllib3
import ipaddress

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://localhost:5555/api/"
ADMIN_PASS = "admin123"
START_IP = "192.168.30.50"


    
payload = {
    "jsonrpc": "2.0",
    "id": "1",
    "method": "CreateUser",
    "params": {
        "HubName_str": "DEFAULT",
        "Name_str": "test1",
        "AuthType_u32": 1,
        "Auth_Password_str": "test1",
        "UsePolicy_bool": True,
        "policy": {
            "IPAddress_str": START_IP,
            "SubnetMask_str": "255.255.255.0",
            "MaxConnection_u32": 1 
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
        print(f"Utilisateur test1 créé avec l'IP : {START_IP}")
except Exception as e:
    print(f"Erreur réseau : {e}")

