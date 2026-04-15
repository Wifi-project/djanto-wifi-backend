import httpx
import json


async def create_vpn_user(username, password, ip):

    url = "https://localhost:5555/api/"
    

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
                "IPAddress_str": ip,
                "SubnetMask_str": "255.255.0.0"
            }
        }
    }

    headers = {"X-VPNADMIN-PASSWORD": "admin123"}
    async with httpx.AsyncClient as client:
        try:
        
            response = await client.post(url, json=payload, headers=headers, verify=False)
            data = response.json()
            
            if "error" in data:
                print(f"Erreur : {data['error']['message']}")
            else:
                await set_password(username, password)
                
        except Exception as e:
            print(f"Erreur réseau : {e}")


async def set_password(username, password):
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
    async with httpx.AsyncClient as client:
        try:
            response = await client.post(url, json=payload, headers={"X-VPNADMIN-PASSWORD": "admin123"}, verify=False)
            return response
        except Exception as e:
            pass 
