# # Installer les paquets
# pip install celery redis django-celery-beat django-celery-results

# # Démarrer Redis (Windows avec WSL ou Docker)
# docker run -d -p 6379:6379 redis

# # Démarrer Celery
# celery -A app worker -l info

# # Démarrer Celery Beat
# celery -A app beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler




# from celery import shared_task
# from celery.utils.log import get_task_logger
# from .models import Client
# from .services import ClientService

# logger = get_task_logger(__name__)

# @shared_task(
#     name="clients.tasks.block_client_async_task",
#     bind=True,                             # 1. Permet d'accéder à l'instance de la tâche (self)
#     autoretry_for=(Exception,),            # 2. Réessaye automatiquement pour n'importe quelle exception
#     max_retries=5,                         # 3. Nombre maximum de tentatives (ici 5 essais max)
#     retry_backoff=True,                    # 4. Attend de plus en plus longtemps entre chaque essai (Backoff)
#     retry_backoff_max=300,                 # 5. N'attend jamais plus de 5 minutes (300s) entre deux essais
# )
# def block_client_async_task(self, client_id: int): # Ajoute 'self' en premier argument grâce à bind=True
#     # Tu peux afficher le numéro de la tentative actuelle dans tes logs Docker
#     logger.info(f"[Celery] Tentative {self.request.retries + 1}/{self.max_retries} pour le client ID : {client_id}")
    
#     try:
#         client = Client.objects.select_related('microtik', 'microtik__subscriptionwg').get(id=client_id)
#         microtik = client.microtik
#         vpn = microtik.subscriptionwg
        
#         result = ClientService.blocked_unlocked_client_service(
#             microtik=microtik,
#             user_slug=client.slug,
#             is_desable=True,
#             vpn=vpn
#         )
        
#         # ⚠️ TRÈS IMPORTANT : Si ton service renvoie un dictionnaire d'échec au lieu de lever une exception,
#         # Celery ne sait pas que ça a échoué. Il faut donc lever une exception manuellement pour déclencher le retry !
#         if result.get("status") != "success":
#             raise Exception(f"Le routeur a refusé l'opération : {result.get('message')}")
            
#         logger.info(f"[Celery] Succès : Client {client.code_username} bloqué.")
#         return "Success"

#     except Client.DoesNotExist:
#         # Si le client n'existe pas en BDD, ça ne sert à rien de réessayer, on stoppe tout.
#         logger.error(f"[Celery] Erreur définitive : Le client {client_id} n'existe pas.")
#         return "Client introuvable."