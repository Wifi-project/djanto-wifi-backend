from app.gdms.api_gdms import gdms_service
from asgiref.sync import async_to_sync

# 1. Récupération de la liste des réseaux
networks_response = async_to_sync(gdms_service.list_networks)(page_num=1, page_size=1000)

# Extraction de la liste des réseaux selon la structure de ta réponse


missing_networks = [
    {"id": 322467, "name": "STALINE WIFI ZONE"},
    {"id": 322755, "name": "MAMOUDOU WIFI ZONE"},
    {"id": 322996, "name": "CISSÉ WIFI ZONE"},
    {"id": 323288, "name": "O.CONDE WIFI ZONE"},
    {"id": 323299, "name": "BOBO WIFI ZONE"},
    {"id": 323834, "name": "MASSINA WIFI ZONE"},
    {"id": 324010, "name": "ABOU OURY WIFI ZONE"},
]
# networks_list = networks_response.get("data", {}).get("result", [])
networks_list = missing_networks

print(f"--- Analyse de {len(networks_list)} réseaux ---")

# 2. Boucle sur chaque réseau pour récupérer ses infos et ses SSID
for net in networks_list:
    network_id = net.get("id")
    network_name = net.get("networkName")
    
    # Appel pour récupérer les SSIDs de ce réseau spécifique 
    # (Note : si ton API prend network_id en paramètre, adapte l'appel comme ci-dessous)
    try:
        ssids_response = async_to_sync(gdms_service.list_network_ssids)(network_id=network_id)
        
        # Extraction des SSIDs (à adapter selon le format exact retourné par ton API list_network_ssids)
        ssids_data = ssids_response.get("data", []) if isinstance(ssids_response, dict) else ssids_response
        
    except Exception as e:
        ssids_data = f"Erreur de récupération ({e})"

    # Affichage formaté
    print(f"📡 Réseau : {network_name} | ID : {network_id} | SSID(s) : {ssids_data}")