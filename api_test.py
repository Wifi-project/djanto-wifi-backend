import hashlib
import hmac
import time
import requests


class GWNCloudSDK:

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        domain: str = "www.gdms.cloud",
    ):
        self.app_id = app_id.strip()
        self.app_secret = app_secret.strip()
        self.base_url = f"https://{domain}"
        self.access_token = None
        self._authenticate()

    def _generate_signature(self, timestamp: str) -> str:
        """Génère la signature HMAC-SHA256 (appID&timestamp)."""
        message = f"{self.app_id}&{timestamp}"
        signature = hmac.new(
            self.app_secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def _authenticate(self):
        """Authentification OAuth2 auprès de GDMS / GWN Cloud."""
        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(timestamp)

        url = f"{self.base_url}/oapi/v1.0.0/oauth/token"

        # Transmission des clés en query params + body JSON
        params = {
            "appID": self.app_id,
            "timestamp": timestamp,
            "signature": signature,
        }
        payload = {"grant_type": "client_credentials"}

        headers = {"Content-Type": "application/json"}

        response = requests.post(
            url, params=params, json=payload, headers=headers, timeout=10
        )

        if response.status_code != 200:
            raise Exception(
                f"Erreur HTTP {response.status_code}: {response.text}"
            )

        res_data = response.json()

        if (
            res_data.get("retCode") == 0
            and "access_token" in res_data.get("data", {})
        ):
            self.access_token = res_data["data"]["access_token"]
            print(f"🔑 Authentification réussie sur {self.base_url} !")
        else:
            raise Exception(
                f"Échec d'authentification API sur {self.base_url} : {res_data}"
            )

    def request(
        self, endpoint: str, method: str = "POST", payload: dict = None
    ) -> dict:
        """Effectue une requête signée sur l'API."""
        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(timestamp)

        params = {
            "appID": self.app_id,
            "timestamp": timestamp,
            "signature": signature,
            "access_token": self.access_token,
        }

        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}

        response = requests.request(
            method,
            url,
            params=params,
            json=payload or {},
            headers=headers,
            timeout=10,
        )
        return response.json()

    def get_networks(self, page_num: int = 1, page_size: int = 100) -> list:
        res = self.request(
            "/oapi/v1.0.0/network/list",
            payload={"pageNum": page_num, "pageSize": page_size},
        )
        return res.get("data", {}).get("result", [])


# ============================================================
# EXÉCUTION AVEC DÉTECTION DU DOMAINE
# ============================================================

if __name__ == "__main__":
    APP_ID = "668208"
    APP_SECRET = "lQeF3M2RzdWA4DZyTBMXGsruCaIOmGo4"

    # Liste des domaines GDMS / GWN Cloud selon les serveurs
    DOMAINES_A_TESTER = [
        "www.gdms.cloud",
        "eu.gdms.cloud",
        "www.gwn.cloud",
        "media.gdms.cloud",
    ]

    sdk = None
    for domain in DOMAINES_A_TESTER:
        try:
            print(f"Tentative de connexion sur {domain}...")
            sdk = GWNCloudSDK(
                app_id=APP_ID, app_secret=APP_SECRET, domain=domain
            )
            break
        except Exception as e:
            print(f"  ❌ Échec sur {domain}: {e}")

    if sdk:
        print("\n Récupération des réseaux...")
        networks = sdk.get_networks()
        print(f"Réseaux trouvés : {networks}")
    else:
        print(
            "\n Échec sur tous les domaines. Vérifiez 'APP_ID' et 'APP_SECRET' sur votre console GDMS."
        )