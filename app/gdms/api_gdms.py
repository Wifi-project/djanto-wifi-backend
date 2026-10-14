import hashlib
import json
import time
import os
from typing import Any

from app.api_extern.baseService import BaseService
from app.utils.get_api import post_data, get_data, StatusRequest
from app.api_extern.auth_manager import auth
from django.utils import timezone
from datetime import timedelta, datetime

class GdmsService(BaseService):
    def __init__(self):
        self.BASE_URL = os.getenv('GWN_DOMAIN','https://www.gwn.cloud')
        self.code = "GDMS"
        self.secret_key = os.getenv("SECRET_KEY","lQeF3M2RzdWA4DZyTBMXGsruCaIOmGo4")
        self.app_id = os.getenv('APP_ID',"668208")
        self.admin_user_id = int(os.getenv("ADMIN_USER_ID",153246)) 
        self.organization_id = int(os.getenv("ORGANIZATION_ID",163540)) 

    # ============================================================
    # URLS
    # ============================================================
    def urls(self, url: str) -> str | None:
        GWN_ENDPOINTS = {
            "token": "/oauth/token",
            "network_create": "/oapi/v1.0.0/network/create",
            "network_list": "/oapi/v1.0.0/network/list",
            "network_delete": "/oapi/v1.0.0/network/delete",
            "network_update": "/oapi/v1.0.0/network/update",
            "ap_add": "/oapi/v1.0.0/ap/add",
            "ap_list": "/oapi/v1.0.0/ap/list",
            "device_reset": "/oapi/v1.0.0/ap/reset",
            "device_reboot": "/oapi/v1.0.0/device/reboot",
            "device_info": "/oapi/v1.0.0/ap/info",
            "device_delete": "/oapi/v1.0.0/ap/delete",
            "ssid_create": "/oapi/v1.0.0/ssid/create",
            "ssid_update": "/oapi/v1.0.0/ssid/update",
            "ssid_delete": "/oapi/v1.0.0/ssid/delete",
            "client_list": "/oapi/v1.0.0/client/list",
            "client_retrieve": "/oapi/v1.0.0/client/info",
            "client_block": "/oapi/v1.0.0/client/block",
            "client_online": "/oapi/v1.0.0/portal/monitor/list",
            "client_kick": "/oapi/v1.0.0/portal/kick",
            "voucher_group_list": "/oapi/v1.0.0/voucher/list",
            "voucher_in_group": "/v1.0.0/voucher/vouchers/list",
            "voucher_renew": "v1.0.0/voucher/vouchers/renew",
            "voucher_create": "/oapi/v1.0.0/voucher/save",
            "voucher_delete": "/oapi/v1.0.0/voucher/delete",
            "voucher_status": "/v1.0.0/voucher/vouchers/states",
        }
        return f"{self.BASE_URL}{GWN_ENDPOINTS.get(url)}"

    def code_response(self, action: str, code: int) -> str | None:
        code_map = {
            'network': {
                50006: "(Permission refusée)",
                21004: "refus de clonage de l'identifiant réseau",
                21003: "le code pays du réseau est nul",
                21002: "le fuseau horaire du réseau est nul",
                20004: "le nom du réseau existe déjà",
                21000: "le nom du réseau est vide",
                20007: "le réseau actuel n'existe pas",
                21001: "l'identifiant du réseau est nul",
                20009: "le réseau a été supprimé",
                20010: "le réseau n'a pas d'autorité",
            },
            'app_device': {
                50101: "la version de l'appareil n'est pas prise en charge",
                30006: "erreur de mot de passe",
                30008: "le point d'accès n'existe pas",
                30012: "le point d'accès est déjà associé à un autre compte",
                30005: "le point d'accès est déjà associé au réseau actuel",
                50004: "erreur de service",
                50005: "paramètre invalide",
                47404: "le groupe d'appareils n'existe pas",
                19005: "paramètres manquants",
                20002: "le point d'accès est hors ligne",
                50007: "adresse MAC invalide",
            },
            'ssid': {
                70003: "l'identifiant SSID est vide",
                70005: "le SSID n'a pas d'autorité",
                70006: "le SSID n'existe pas !",
                70011: "bridge et NAT ne peuvent pas être activés en même temps",
                20004: "le nom du réseau existe déjà",
                20006: "n'a pas d'autorité dans ce réseau",
                21001: "l'identifiant du réseau est nul",
            },
            'client': {
                47404: "le groupe d'appareils n'existe pas",
                50005: "paramètre invalide",
                50007: "adresse MAC invalide",
                40001: "le client n'existe pas",
                50004: "erreur de service",
                40004: "longueur du client erronée, 0-64",
                50003: "échec de l'authentification",
                19001: "horodatage invalide",
            },
            'voucher': {
                50005: "paramètre invalide",
                16024: "le voucher ne peut pas être supprimé lorsqu'il est en cours d'utilisation !",
                16016: "le voucher n'existe pas !",
                16032: "le nombre de vouchers dépasse la limite",
                16031: "erreur de format du mot de passe du voucher",
                16030: "le mot de passe du voucher est requis",
                16029: "le mot de passe du voucher existe déjà",
                16014: "le nom du groupe de vouchers existe déjà !",
                16013: "erreur d'échelle des minutes !",
                16012: "erreur d'échelle des heures !",
                16011: "erreur d'échelle des jours !",
                16010: "la durée effective ne peut pas être nulle !",
                16009: "la durée effective ne peut pas être vide !",
                16007: "les notes du voucher sont trop longues !",
                16006: "erreur d'échelle de validité du voucher !",
                16003: "erreur d'échelle du nombre d'appareils du voucher !",
                16002: "erreur de format du nom du voucher !",
                16001: "erreur d'échelle du numéro du voucher !",
            },
        }

        service = code_map.get(action)
        if not service:
            return None

        return service.get(code, 'une erreur inconue')

    def response(self,data:Any,status:bool=True) -> dict[str, str]:
        return {
            'status': status,
            'data': data
        }

    # ============================================================
    # AUTH
    # ============================================================
    async def authentication(self) -> str | None:
        url = self.urls(url="token")

        params = {
            "grant_type": "client_credentials",
            "client_id": self.app_id,
            "client_secret": self.secret_key,
        }

        response = await get_data(url=url, params=params)

        if response.get("status") == StatusRequest.success.value:
            data = response.get("message") or {}
            return data.get("access_token")
        return None


    async def get_token(self) -> str | None:
        return await auth(
            call_aut=self.authentication,
            code=self.code,
            expire_time_init=10516,
        )

    # ============================================================
    # SIGNATURE + REQUÊTE GÉNÉRIQUE
    # ============================================================
    async def signature(self, token: str, timestamp: str, payload: dict | None = None) -> str:
        params_str = (
            f"access_token={token}&"
            f"appID={self.app_id}&"
            f"secretKey={self.secret_key}&"
            f"timestamp={timestamp}"
        )

        if payload is not None:
            body_json_str = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
            body_hash = hashlib.sha256(body_json_str.encode("utf-8")).hexdigest()
            string_to_sign = f"&{params_str}&{body_hash}&"
        else:
            string_to_sign = f"&{params_str}&"

        return hashlib.sha256(string_to_sign.encode("utf-8")).hexdigest().lower()


    async def send_request(self, url: str, payload: dict | None = None,action:str|None=None) -> dict:
        timestamp = str(int(time.time() * 1000))

        token = await self.get_token()
        if not token:
            raise ValueError("Impossible d'obtenir un token GDMS")

        signature = await self.signature(token=token, timestamp=timestamp, payload=payload)

        query_url = (
            f"{url}?"
            f"access_token={token}&"
            f"appID={self.app_id}&"
            f"timestamp={timestamp}&"
            f"signature={signature}"
        )

        headers = {"Content-Type": "application/json;charset=UTF-8"}

        json_payload = (
            json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
            if payload is not None
            else None
        )

        response = await post_data(url=query_url, payload=json_payload, headers=headers,is_data=True)
        print("------la send",response)
        if response.get("status") != StatusRequest.success.value:
            return self.response(data=f'{response}', status=False)

        msg = response.get("message") or {}
        if msg:
            r_code = msg.get("retCode")
            if r_code == 0:
                return self.response(data=msg.get('data'), status=True)
            
            code = self.code_response(action=action,code=r_code)
            return self.response(data=code, status=False)

        
        return self.response(data=f'une erreur inconue {response}',status=False)

    # ============================================================
    # 1. NETWORKS
    # ============================================================
    async def create_network(self, network_name: str) -> int | None:
        admin_user_id = self.admin_user_id
        organization_id = self.organization_id
        url = self.urls(url="network_create")

        payload = {
            "networkName": network_name,
            "country": "GN",
            "timezone": "Etc/GMT",
            "networkAdministrators": [int(admin_user_id)],
            "organizationId": int(organization_id),
        }

        res = await self.send_request(url=url, payload=payload,action='network')
        if res.get("status"):
            id = res.get("data")
            return id
        return res


    async def list_networks(self, page_num: int = 1, page_size: int = 100) -> dict:
        url = self.urls(url="network_list")
        payload = {"pageNum": page_num, "pageSize": page_size}
        return await self.send_request(url=url, payload=payload,action='network')


    async def update_network(self,network_id:int,network_name:str) -> dict:
        admin_user_id = self.admin_user_id
        organization_id = self.organization_id

        url = self.urls(url='network_update')
        payload = {
                "id": network_id,
                "networkName": network_name,
                "country": "GN",
                "timezone": "Etc/GMT",
                "networkAdministrators": [int(admin_user_id)],
                "organizationId": int(organization_id),
            }

        return await self.send_request(url=url, payload=payload,action='network')


    async def delete_nework(self,network_id:int) -> dict:
        url = self.urls(url='network_delete')
        payload = {
            'id': network_id
        }
        return await self.send_request(url=url, payload=payload, action='network')


    # ============================================================
    # 2. DEVICES / AP
    # ============================================================
    async def device_add_ap(self, network_id: int, mac: str, password: str, name: str) -> str:
        url = self.urls(url="ap_add")
        payload = {
            "networkId": network_id,
            "name": name,
            "password": password,
            # "mac": mac.upper(),
            "mac": mac,
        }

        return await self.send_request(url=url, payload=payload,action='app_device')


    async def device_list_aps(self, network_id: int, page_num: int = 1, page_size: int = 100) -> dict:
        url = self.urls(url="ap_list")
        payload = {
            "networkId": network_id,
            "pageNum": page_num,
            "pageSize": page_size,
        }
        return await self.send_request(url=url, payload=payload, action='app_device')


    async def device_reboot_aps(self, network_id: int, mac_list: list) -> str:
        url = self.urls(url="device_reboot")
        payload = {"macs": mac_list}
        return await self.send_request(url=url, payload=payload,action="app_device")


    async def device_info(self, network_id: int, mac_list: list | None = None) -> dict:
        url = self.urls(url="device_info")
        payload = {"macs": mac_list}
        return await self.send_request(url=url, payload=payload, action="app_device")


    async def device_delete(self,mac_list:list) -> dict:
        url = self.urls(url='device_delete')
        payload = {
            'mac': mac_list
        }
        return await self.send_request(url=url, payload=payload,action="app_device")


    # ============================================================
    # 3. SSIDs
    # ============================================================
    async def create_ssid(self, network_id: int, ssid_name: str) -> int | None:
        url = self.urls(url="ssid_create")
        portal_id = os.getenv("PORTAIL_ID")

        payload = {
            "networkId": network_id,
            "ssidSsid": ssid_name,
            "ssidSecurityType": 0,
            "ssidPortalEnable": 1,
            "ssidPortalPolicy": portal_id,
            "scheduleId": 0,
        }

        response = await self.send_request(url=url, payload=payload,action="ssid")
        return response.get("id")


    async def update_ssid(
        self,
        network_id: int,
        ssid_id: int,
        new_name: str | None = None,
        current_ssid_name: str = "",
    ) -> str:
        url = self.urls(url="ssid_update")
        ssid_name = new_name or current_ssid_name

        payload = {
            "id": ssid_id,
            "ssidSsid": ssid_name,
            "ssidWepKey": "",
            "ssidWpaKey": "",
            "bindMacs": [],
            "ssidTimedClientPolicy": 0,
            "networkId": network_id,
        }

        return await self.send_request(url=url, payload=payload,action="ssid")


    async def block_unblock_ssid(
        self,
        network_id: int,
        ssid_id: int,
        current_ssid_name: str,
        block: bool = True,
    ) -> str:
        url = self.urls(url="ssid_update")
        payload = {
            "id": ssid_id,
            "ssidSsid": current_ssid_name,
            "ssidWepKey": "",
            "ssidWpaKey": "",
            "bindMacs": [],
            "ssidTimedClientPolicy": 0,
            "networkId": network_id,
            "ssidEnable": 0 if block else 1,
        }
        
        return await self.send_request(url=url, payload=payload,action="ssid")


    async def set_client_isolation(
        self,
        network_id: int,
        ssid_id: int,
        ssid_name: str,
        enable: bool = True,
    ) -> str:
        url = self.urls(url="ssid_update")
        payload = {
            "id": ssid_id,
            "ssidSsid": ssid_name,
            "ssidWepKey": "",
            "ssidWpaKey": "",
            "bindMacs": [],
            "ssidTimedClientPolicy": 0,
            "networkId": network_id,
            "ssidIsolation": 1 if enable else 0,
            "ssidIsolationMode": 1 if enable else 0,
        }
        return await self.send_request(url=url, payload=payload,action="ssid")
        

    # ============================================================
    # 4. CLIENTS
    # ============================================================
    async def list_clients(
            self, network_id: int, page_num: int = 1, 
            page_size: int = 100,start_at:str|None=None,
            end_date:str | None = None ) -> dict:

        yesterday = timezone.now() - timedelta(days=1)
        now = timezone.now()
        timestamp_ms = int(now.timestamp() * 1000)
        yesterday_ms = int(yesterday.timestamp() * 1000)
        
        url = self.urls(url="client_list")
        payload = {
            "networkId": network_id,
            "pageNum": page_num,
            "pageSize": page_size,
            "type": "desc",
            "order": "ip",
            "search": "ap",
            "endDate": start_at or yesterday_ms,
            "startDate": end_date or timestamp_ms
        }
        return await self.send_request(url=url, payload=payload,action="client")


    async def block_disblock_client(self, network_id: int, client_id: str, enable: bool = True) -> str:
        url = self.urls(url="client_block")
        payload = {
            "block": 0 if enable else 1,
            "clientId": client_id,
            "networkId": network_id,
        }
        return await self.send_request(url=url, payload=payload,action="client")


    async def client_retrieve(self, network_id: int, client_id: str) -> dict:
        url = self.urls(url="client_retrieve")
        payload = {"clientId": client_id, "networkId": network_id}
        return await self.send_request(url=url, payload=payload,action="client")


    def get_online_guests(self, network_id: int, page_num: int = 1, page_size: int = 20) -> dict:
        """
        Récupère la liste des invités actuellement connectés au portail captif.
        
        """
        url = self.urls(url='client_online')
                
        payload = {
            "networkId": network_id,
            "pageNum": page_num,
            "pageSize": page_size,
            "order": "loginTimeStr",
            "type": "descending"
        }
                    
        response = self.send_request(url=url,payload=payload, action="client")
        return response


    def kick_guest(self, ap_mac: str, client_mac: str, ssid_name: str) -> dict:
        """
        Expulse (déconnecte) un client spécifique d'une borne Wi-Fi (AP).
        """
        url = self.urls(url='kick_client')
        
        payload = {
            "mac": ap_mac,           
            "client_mac": client_mac, 
            "ssid_name": ssid_name   
        }
        
        response = self.send_request(url=url,payload=payload,action="client")
        return response


    # ============================================================
    # 5. VOUCHERS
    # ============================================================
    async def list_group_voucher(self, network_id: int, page_num: int, page_size: int,search:str) -> dict:
        url = self.urls(url="voucher_group_list")
        payload = {
            "search": search,
            "order": "createTimeStr",
            "pageNum": page_num,
            "pageSize": page_size,
            "networkId": network_id,
        }
        return await self.send_request(url=url, payload=payload,action="voucher")


    async def list_voucher_in_group(self, search:str,group_id:int,nework_id:int) -> dict[str,str]:
        url = self.urls(url='voucher_in_group')
        payload = {
                "search": "",
                "order": "",
                "type": "desc",
                "pageNum": 1,
                "pageSize": 10,
                "filter": {
                    "state": ""
                },
                "groupId": group_id,
                "networkId": nework_id
            }

        return await self.send_request(url=url,payload=payload,action='voucher')


    async def create_vouchers(
        self,
        network_id: int,
        upRate: int,
        downRate: int,
        name: str = "Lot_Vouchers1",
        count: int = 1,
        effect_duration_map: dict = {'d':0,'h':0,'m':30},
        max_devices: int = 1,
        expiration_days: int = 30,
        length: int = 8,
        voucher_format: int = 0,
    ) -> dict:
        url = self.urls(url="voucher_create")
        payload = {
            "networkId": network_id,
            "name": name,
            "vocherNum": count,
            "upRate": upRate,
            "downRate": downRate,
            "deviceNum": max_devices,
            "expiration": expiration_days,
            "effectDurationMap": effect_duration_map,
            "voucherLength": length,
            "voucherFormat": voucher_format,
            "usageLimitType": 0,
            "voucherType": 0,
        }
        return await self.send_request(url=url, payload=payload,action="voucher")


    async def renew_voucher(self,network_id:int,voucher_id:int) -> dict[str,str]:
        url = self.urls(url='voucher_renew')
        payload = {
            "networkId": network_id,
            "id": voucher_id
        }

        await self.send_request(url=url, payload=payload, action='voucher')


    async def delete_voucher(self, network_id: int, voucher_id: int) -> dict:
        url = self.urls(url="voucher_delete")
        payload = {"id": voucher_id, "networkId": network_id}
        return await self.send_request(url=url, payload=payload,action="voucher")


gdms_service = GdmsService()


##########################################################
# POUR LES TASKS
#########################################################

async def provision_gdms(
        network_name:str, 
        mac:str, 
        ap_password:str, 
        device_name:str, 
        ssid_name:str,
        subwg_slug:str
        ):
    
    service = GdmsService()
    subscription = await SubscriptionWG.objects.filter(slug=subwg_slug).afirst()

    network_id = None 

    if not subscription.gdms_network_id:
        network_id = await service.create_network(network_name=network_name)
        subscription.gdms_network_id = network_id
        await subscription.asave(update_fields=['gdms_network_id'])
    else: 
        network_id = subscription.gdms_network_id

    if not subscription.device_name:
        await service.device_add_ap(
            network_id=network_id,
            mac=mac,
            password=ap_password,
            name=device_name,
        )
        subscription.device_name = device_name
        await subscription.asave(update_fields=['device_name'])

    ssid_id = await service.create_ssid(
        network_id=network_id,
        ssid_name=ssid_name
    )
    subscription.gdms_site_id = ssid_id
    await subscription.asave(update_fields=["gdms_site_id"])

    return {"network_id": network_id, "ssid_id": ssid_id}