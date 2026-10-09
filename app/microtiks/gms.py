import hashlib
import json
import time
import os
from typing import Any

from app.api_extern.baseService import BaseService
from app.utils.get_api import post_data, get_data, StatusRequest
from app.api_extern.auth_manager import auth
from app.subscriptions.models import SubscriptionWG


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
            "ap_add": "/oapi/v1.0.0/ap/add",
            "ap_list": "/oapi/v1.0.0/ap/list",
            "device_reset": "/oapi/v1.0.0/ap/reset",
            "device_reboot": "/oapi/v1.0.0/device/reboot",
            "device_info": "/oapi/v1.0.0/ap/info",
            "ssid_create": "/oapi/v1.0.0/ssid/create",
            "ssid_update": "/oapi/v1.0.0/ssid/update",
            "ssid_delete": "/oapi/v1.0.0/ssid/delete",
            "client_list": "/oapi/v1.0.0/client/list",
            "client_retrieve": "/oapi/v1.0.0/client/info",
            "client_block": "/oapi/v1.0.0/client/block",
            "client_online": "/oapi/v1.0.0/portal/monitor/list",
            "client_kick": "/oapi/v1.0.0/portal/kick",
            "voucher_list": "/oapi/v1.0.0/voucher/list",
            "voucher_create": "/oapi/v1.0.0/voucher/save",
            "voucher_delete": "/oapi/v1.0.0/voucher/delete",
            "voucher_status": "/v1.0.0/voucher/vouchers/states",
        }
        return f"{self.BASE_URL}{GWN_ENDPOINTS.get(url)}"

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


    async def send_request(self, url: str, payload: dict | None = None) -> dict:
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

        if response.get("status") != StatusRequest.success.value:
            raise ValueError(f"Erreur HTTP GDMS : {response.get('message', 'inconnue')}")

        msg = response.get("message") or {}
        if msg.get("retCode") != 0:
            raise ValueError(f"Erreur GDMS : {msg.get('msg', 'inconnue')}")

        return msg.get("data", {})

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

        res = await self.send_request(url=url, payload=payload)
        return res.get("id")

    async def list_networks(self, page_num: int = 1, page_size: int = 100) -> dict:
        url = self.urls(url="network_list")
        payload = {"pageNum": page_num, "pageSize": page_size}
        return await self.send_request(url=url, payload=payload)

    # ============================================================
    # 2. DEVICES / AP
    # ============================================================
    async def device_add_ap(self, network_id: int, mac: str, password: str, name: str) -> str:
        url = self.urls(url="ap_add")
        payload = {
            "networkId": network_id,
            "name": name,
            "password": password,
            "mac": mac.upper(),
        }
        await self.send_request(url=url, payload=payload)
        return StatusRequest.success.value

    async def device_list_aps(self, network_id: int, page_num: int = 1, page_size: int = 100) -> dict:
        url = self.urls(url="ap_list")
        payload = {
            "networkId": network_id,
            "pageNum": page_num,
            "pageSize": page_size,
        }
        return await self.send_request(url=url, payload=payload)

    async def device_reboot_aps(self, network_id: int, mac_list: list) -> str:
        url = self.urls(url="device_reboot")
        payload = {"macs": mac_list}
        await self.send_request(url=url, payload=payload)
        return StatusRequest.success.value

    async def device_info(self, network_id: int, mac_list: list | None = None) -> dict:
        url = self.urls(url="device_info")
        payload = {"macs": mac_list}
        return await self.send_request(url=url, payload=payload)

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

        response = await self.send_request(url=url, payload=payload)
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

        await self.send_request(url=url, payload=payload)
        return StatusRequest.success.value

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
        await self.send_request(url=url, payload=payload)
        return StatusRequest.success.value

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
        await self.send_request(url=url, payload=payload)
        return StatusRequest.success.value

    # ============================================================
    # 4. CLIENTS
    # ============================================================
    async def list_clients(self, network_id: int, page_num: int = 1, page_size: int = 100) -> dict:
        url = self.urls(url="client_list")
        payload = {
            "networkId": network_id,
            "pageNum": page_num,
            "pageSize": page_size,
            "type": "desc",
        }
        return await self.send_request(url=url, payload=payload)

    async def block_disblock_client(self, network_id: int, client_id: str, enable: bool = True) -> str:
        url = self.urls(url="client_block")
        payload = {
            "block": 0 if enable else 1,
            "clientId": client_id,
            "networkId": network_id,
        }
        await self.send_request(url=url, payload=payload)
        return StatusRequest.success.value

    async def client_retrieve(self, network_id: int, client_id: str) -> dict:
        url = self.urls(url="client_retrieve")
        payload = {"clientId": client_id, "networkId": network_id}
        return await self.send_request(url=url, payload=payload)


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
                    
        response = self.send_request(url=url,payload=payload)
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
        
        response = self.send_request(url=url,payload=payload)
        return response


    # ============================================================
    # 5. VOUCHERS
    # ============================================================
    async def list_voucher(self, network_id: int, page_num: int, page_size: int) -> dict:
        url = self.urls(url="voucher_list")
        payload = {
            "search": "",
            "order": "createTimeStr",
            "pageNum": page_num,
            "pageSize": page_size,
            "networkId": network_id,
        }
        return await self.send_request(url=url, payload=payload)

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
        return await self.send_request(url=url, payload=payload)

    async def delete_voucher(self, network_id: int, voucher_id: int) -> dict:
        url = self.urls(url="voucher_delete")
        payload = {"id": voucher_id, "networkId": network_id}
        return await self.send_request(url=url, payload=payload)

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