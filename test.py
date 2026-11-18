# import time
# import requests
# from typing import Optional, Dict, Any

# class RuijieCloudClient:
#     def __init__(self, base_url: str, app_id: str, app_secret: str):
#         """
#         Client d'intégration officiel Ruijie Cloud (Basé sur la documentation API).
#         """
#         self.base_url = base_url.rstrip("/")
#         self.app_id = app_id
#         self.app_secret = app_secret
#         self.access_token: Optional[str] = None
#         self.token_expires_at: float = 0.0

#     def authenticate(self) -> str:
#         """
#         Récupère l'access_token via l'endpoint officiel d'authentification.
#         """
#         # Endpoint officiel avec le token de validation requis par l'API Ruijie
#         auth_url = f"{self.base_url}/service/api/oauth20/client/access_token"
#         params = {"token": "d63dss0a81e4415a889ac5b78fsc904a"}
        
#         payload = {
#             "appid": self.app_id,
#             "secret": self.app_secret
#         }
#         headers = {"Content-Type": "application/json"}
        
#         print(f" -> Authentification en cours sur : {auth_url}")
        
#         try:
#             response = requests.post(auth_url, params=params, json=payload, headers=headers, timeout=15)
#             response.raise_for_status()
#             data = response.json()
            
#             # Vérification du code de retour (0 = Succès)
#             if data.get("code") == 0:
#                 # La documentation indique 'accessToken' dans la réponse
#                 self.access_token = data.get("accessToken") or data.get("access_token")
#                 # Le token expire au bout de 30 jours, on met une sécurité de rafraîchissement
#                 self.token_expires_at = time.time() + (86400 * 29) 
#                 print(" [RUIJIE] Authentification réussie ! Token récupéré.")
#                 return self.access_token
#             else:
#                 raise Exception(f"Erreur Ruijie (Code {data.get('code')}): {data.get('msg')}")
                
#         except requests.exceptions.RequestException as e:
#             raise Exception(f"Erreur réseau lors de l'authentification : {e}")

#     def _get_valid_token(self) -> str:
#         if not self.access_token or time.time() >= self.token_expires_at:
#             self.authenticate()
#         return self.access_token

#     def _request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
#         """Effectue une requête RESTful en injectant obligatoirement l'access_token en QueryParam."""
#         token = self._get_valid_token()
#         url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
#         if params is None:
#             params = {}
#         # L'access_token doit obligatoirement être passé dans l'URL (QueryParam)
#         params["access_token"] = token

#         headers = {"Content-Type": "application/json"}
        
#         response = requests.request(
#             method=method.upper(),
#             url=url,
#             params=params,
#             json=json_data,
#             headers=headers,
#             timeout=15
#         )
#         response.raise_for_status()
#         return response.json()

#     # ==========================================
#     # MÉTHODES OFFICIELLES (DOC API)
#     # ==========================================
#     def get_account_info(self) -> Dict[str, Any]:
#         """Récupère les informations du compte tenant (2.1.3)"""
#         return self._request("GET", "service/api/org/account/info")

#     def get_group_tree(self, depth: str = "BUILDING") -> Dict[str, Any]:
#         """Récupère l'arbre des groupes réseau / projets (2.2.1)"""
#         return self._request("GET", "service/api/group/single/tree", params={"depth": depth})


# # ==========================================
# # TEST EN CONSOLE
# # ==========================================
# if __name__ == "__main__":
#     print("=" * 65)
#     print("TEST DE L'API RUIJIE CLOUD (CLOUD-EU) - DJANTOWIFI")
#     print("=" * 65)

#     # Tes identifiants extraits de ton espace développeur
#     APP_ID = "open041d630e4549"
#     APP_SECRET = "56721107272a455c8d2912c03bc4eed4"
#     BASE_URL = "https://cloud-eu.ruijienetworks.com"

#     client = RuijieCloudClient(base_url=BASE_URL, app_id=APP_ID, app_secret=APP_SECRET)

#     try:
#         print("\n1. Test d'authentification...")
#         token = client.authenticate()
#         print(f"Token d'accès : {token[:10]}...")

#         print("\n2. Test de récupération des informations du compte...")
#         account_info = client.get_account_info()
#         print("Compte récupéré avec succès :", account_info)

#         print("\n3. Test de récupération de l'arbre des groupes (Projets)...")
#         groups = client.get_group_tree(depth="BUILDING")
#         print("Groupes/Projets récupérés :", groups)

#         print("\n Tous les tests se sont déroulés avec succès !")

#     except Exception as err:
#         print(f"\n Erreur d'exécution : {err}")