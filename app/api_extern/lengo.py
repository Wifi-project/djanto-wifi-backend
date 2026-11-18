from typing import Optional, Dict, Any
from app.utils.get_api import post_data


class LengoPayClient:
    def __init__(self, license_key: str):
        self.license_key = license_key
        self.base_url_v1 = "https://portal.lengopay.com/api/v1"
        self.base_url_v2 = "https://portal.lengopay.com/api/v2"
        
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Basic {self.license_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def create_payment(
        self, 
        websiteid: str, 
        amount: float, 
        currency: str, 
        country: str = "GN", 
        return_url: Optional[str] = None, 
        failure_url: Optional[str] = None, 
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initie une demande de paiement (v1)"""
        payload = {
            "websiteid": websiteid,
            "amount": amount,
            "currency": currency,
            "country": country,
            "return_url": return_url,
            "failure_url": failure_url,
            "callback_url": callback_url
        }

        cleaned_payload = {k: v for k, v in payload.items() if v is not None}
        return await post_data(
            f"{self.base_url_v1}/payments",
            cleaned_payload,
            headers=self._get_headers(),  # Ajout des parenthèses ici
        )


    async def request_payout(
        self, 
        amount: str, 
        currency: str, 
        websiteid: str, 
        type_account: str, 
        account: str, 
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initie un transfert / Payout (v2)"""
        payload = {
            "amount": amount,
            "currency": currency,
            "websiteid": websiteid,
            "type_account": type_account,
            "account": account,
            "callback_url": callback_url
        }
        cleaned_payload = {k: v for k, v in payload.items() if v is not None}
        
        return await post_data(
            f"{self.base_url_v2}/payout/request", 
            cleaned_payload,
            headers=self._get_headers(), 
        )