# import requests

# WGEASY_API_URL = "http://localhost:51821/api"
# WGEASY_PASSWORD = "admin123"

# def creer_acces_wireguard(point_de_vente_id):
#     from .models import PointDeVente
#     pdv = PointDeVente.objects.get(id=point_de_vente_id)
    
#     session = requests.Session()
    
#     # 1. Connexion à l'API de wg-easy
#     login_resp = session.post(f"{WGEASY_API_URL}/session", json={"password": WGEASY_PASSWORD})
#     if not login_resp.json().get("success"):
#         return {"status": "error", "message": "Échec d'authentification wg-easy"}

#     # 2. Demande de création d'un nouveau Peer (Client WireGuard)
#     payload = {
#         "name": f"client_{pdv.ref_abonnement}"
#     }
#     create_resp = session.post(f"{WGEASY_API_URL}/wireguard/client", json=payload)
#     client_data = create_resp.json()
    
#     # 3. Extraction des clés et de l'IP
#     # wg-easy génère automatiquement la paire de clé et l'IP disponible
#     pdv.wg_client_id = client_data.get("id")
#     pdv.ip_tunnel = client_data.get("address")
#     pdv.cle_privee = client_data.get("privateKey")
#     pdv.cle_publique = client_data.get("publicKey")
#     pdv.est_actif = True
#     pdv.save()
    
#     return {"status": "success", "point_de_vente": pdv}


import routeros_api
# from myapp.models import PointDeVente

def creer_ticket_a_distance(username_ticket, password_ticket):
    # Connexion à travers le tunnel WireGuard fraîchement créé
    connection = routeros_api.RouterOsApiPool(
        host="127.0.0.1", # Utilise l'IP enregistrée en BDD (ex: 10.8.0.2)
        username="admin",
        password="QQQqqq111",
        plaintext_login=True
    )
    
    try:
        api = connection.get_api()
        hotspot_user = api.get_resource('/ip/hotspot/user')
        
        # Ajout du ticket Wi-Fi commandé depuis le site Web
        hotspot_user.add(
            name=username_ticket,
            password=password_ticket,
            profile="24h"
        )
        return {"status": "success", "message": f"Ticket {username_ticket} créé avec succès en province !"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        connection.disconnect()


if __name__ == '__main__':
    # --- BLOC DE TEST LOCAL ---
    print("🚀 Démarrage du script de test d'approvisionnement de ticket...")
    
    # On simule un ticket Wi-Fi généré par votre site e-commerce (ex: id / mot de passe)
    TICKET_TEST_USER = "ticket_guinee_f77"
    TICKET_TEST_PASS = "WiFi2026!Xf"
    
    # Appel de votre fonction de création distante à travers la passerelle réseau
    resultat = creer_ticket_a_distance(
        username_ticket=TICKET_TEST_USER, 
        password_ticket=TICKET_TEST_PASS
    )
    
    # Affichage du résultat dans votre console
    if resultat["status"] == "success":
        print(f"✅ SUCCÈS : {resultat['message']}")
    else:
        print(f"❌ ERREUR : Impossible de créer le ticket. Raison : {resultat['message']}")
