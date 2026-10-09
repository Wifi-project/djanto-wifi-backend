import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Any

import routeros_api

from django.db import transaction
from django.utils import timezone
from django.http import HttpError

from app.api_extern.baseService import BaseService
from app.microtiks.models import Microtik, Profil,RouteurType
from app.clients.models import Client
from app.subscriptions.models import SubscriptionWG
from app.utils.def_utils import parse_mikrotik_rate,generer_code_unique

logger = logging.getLogger(__name__)


class MikrotikService(BaseService):
    """
    Service d'interaction avec les routeurs MikroTik via RouterOS API.
    Inspiré de GdmsService : connexion, ressources, méthodes métier.
    """

    def __init__(self, vpn: SubscriptionWG):
        """
        vpn : SubscriptionWG contenant wg_ip, mikrotik_username, mikrotik_password.
        """
        super().__init__()
        self.BASE_URL = vpn.wg_ip
        self.code = "MIKROTIK"
        self.username = vpn.mikrotik_username
        self.password = vpn.mikrotik_password
        self.vpn = vpn

    # ============================================================
    # MAPPING DES RESSOURCES ROUTEROS
    # ============================================================
    def urls(self, url: str | None = None) -> str | dict | None:
        """
        Mapping des endpoints RouterOS (équivalent de urls() dans GdmsService).
        Si url=None, retourne tout le mapping (utile pour debug).
        """
        RESOURCES = {
            "hotspot_user": "/ip/hotspot/user",
            "hotspot_profile": "/ip/hotspot/user/profile",
            "hotspot_active": "/ip/hotspot/active",
            "hotspot_user_reset": "/ip/hotspot/user/reset-counters",
            "ppp_secret": "/ppp/secret",
            "ppp_profile": "/ppp/profile",
        }
        if url is None:
            return RESOURCES
        return RESOURCES.get(url)

    # ============================================================
    # AUTH / SIGNATURE → adaptés MikroTik (no-op ou validation)
    # ============================================================
    async def authentication(self) -> dict:
        """
        MikroTik utilise Basic Auth au niveau du pool.
        On retourne juste les credentials (utile pour la cohérence de l'interface).
        """
        if not self.username or not self.password:
            raise ValueError("Username/Password MikroTik manquants.")
        return {
            "host": self.BASE_URL,
            "username": self.username,
            "port": 8728,
        }

    def signature(self):
        """Pas de signature pour MikroTik → no-op."""
        return None

    async def send_request(self, *args, **kwargs):
        """
        Adapté : pour MikroTik, 'send_request' = ouvrir une connexion API.
        On garde la signature pour compatibilité avec BaseService.
        """
        return self.connect()

    # ============================================================
    # CONNEXION (remplace send_request)
    # ============================================================
    def connect(self) -> dict:
        """
        Ouvre une connexion RouterOS API.
        Retourne {"status": bool, "pool": ..., "api": ..., "message": ...}
        """
        pool = routeros_api.RouterOsApiPool(
            host=self.BASE_URL,
            username=self.username,
            password=self.password,
            port=8728,
            plaintext_login=True,
        )
        try:
            api = pool.get_api()
            return {"status": True, "pool": pool, "api": api}
        except Exception as e:
            try:
                pool.disconnect()
            except Exception:
                pass
            logger.error("MikroTik connect error: %s", e)
            return {
                "status": False,
                "message": f"Erreur de connexion VPN/API. *** {e}",
            }

    @contextmanager
    def session(self):
        """
        Context manager : ouvre une session, garantit la fermeture du pool.
        Usage :
            with self.session() as (pool, api):
                ...
        """
        res = self.connect()
        if not res["status"]:
            raise ConnectionError(res["message"])
        pool, api = res["pool"], res["api"]
        try:
            yield pool, api
        finally:
            try:
                pool.disconnect()
            except Exception:
                pass

    # ============================================================
    # 1. PROFILS HOTSPOT
    # ============================================================
    def create_profil(self, data: dict, microtik: Microtik) -> dict:
        """
        Crée un profil Hotspot sur le MikroTik + en BDD.
        """
        wg = microtik.subscriptionwg

        type_session = data.pop("type_session", "h")
        duration = data.pop("duration", 1)
        session_timeout, session_timeout_dict = profil_duration(
            duration=duration, type_session=type_session
        )
        price = data.get("price", 0.00)

        try:
            with self.session() as (pool, api):
                profiles = api.get_resource(self.urls("hotspot_profile"))

                profile_name = data.get("name", "default_profil")
                rate_limit = data.get("rate_limit", "512k/1M")
                shared_users = str(data.get("shared_users", 1))
                up_rate, down_rate = parse_mikrotik_rate(rate_limit)

                profiles.add(
                    name=profile_name,
                    rate_limit=rate_limit,
                    shared_users=shared_users,
                    session_timeout=session_timeout,
                )

                Profil.objects.create(
                    name=profile_name,
                    rate_limit=rate_limit,
                    shared_users=int(shared_users),
                    session_timeout=session_timeout,
                    session_timeout_dict=session_timeout_dict,
                    price=price,
                    microtik=microtik,
                    up_rate=up_rate,
                    down_rate=down_rate,
                )

                return {
                    "status": "success",
                    "message": "Profil créé avec succès sur le MikroTik et en BDD",
                }

        except Exception as e:
            logger.error("create_profil error: %s", e)
            return {"status": "failed", "message": f"Création du profil échouée : {e}"}

    def update_profil(self, microtik: Microtik, slug_profil: str, data: dict) -> dict:
        profil = microtik.profils.filter(slug=slug_profil).first()
        if not profil:
            raise HttpError(
                status_code=400,
                message="Aucun profil correspondant à ce slug.",
            )

        type_session = data.pop("type_session", None)
        duration = data.pop("duration", None)

        session_timeout = None
        if type_session and duration:
            session_timeout, _ = profil_duration(
                duration=duration, type_session=type_session
            )

        try:
            with self.session() as (pool, api):
                profiles = api.get_resource(self.urls("hotspot_profile"))
                all_profiles = profiles.get()

                profil_existant = next(
                    (p for p in all_profiles if p.get("name") == profil.name),
                    None,
                )
                if not profil_existant:
                    return {
                        "status": "failed",
                        "message": "Le profil n'a pas été trouvé sur le MikroTik.",
                    }

                profiles.set(
                    id=profil_existant["id"],
                    name=data.get("name", profil.name),
                    rate_limit=data.get("rate_limit", profil.rate_limit),
                    shared_users=str(data.get("shared_users", profil.shared_users)),
                    session_timeout=session_timeout or profil.session_timeout,
                )

                if session_timeout:
                    profil.session_timeout = session_timeout

                for key, value in data.items():
                    if hasattr(profil, key):
                        setattr(profil, key, value)
                profil.save()

                return {"status": "success", "message": "Profil modifié avec succès."}

        except Exception as e:
            logger.error("update_profil error: %s", e)
            return {"status": "failed", "message": f"Modification échouée : {e}"}

    def delete_profil(self, microtik: Microtik, profil_slug: str) -> dict:
        profil = microtik.profils.filter(slug=profil_slug).first()
        if not profil:
            raise HttpError(
                status_code=400,
                message="Aucun profil correspondant à ce slug.",
            )

        try:
            with self.session() as (pool, api):
                profiles = api.get_resource(self.urls("hotspot_profile"))
                all_profiles = profiles.get()

                profil_existant = next(
                    (p for p in all_profiles if p.get("name") == profil.name),
                    None,
                )
                if profil_existant:
                    profiles.remove(id=profil_existant["id"])

                profil.delete()
                return {"status": "success", "message": "Profil supprimé avec succès."}

        except Exception as e:
            logger.error("delete_profil error: %s", e)
            return {"status": "failed", "message": f"Suppression échouée : {e}"}

    def list_profils(self, microtik_slug: str):
        microtik = Microtik.objects.filter(slug=microtik_slug).first()
        if not microtik:
            return []
        return microtik.profils.all()

    def sync_profils_to_db(self, microtik_slug: str) -> dict:
        """
        Récupère les profils Hotspot du MikroTik et les upsert en BDD.
        """
        try:
            microtik = Microtik.objects.get(slug=microtik_slug)
        except Microtik.DoesNotExist:
            return {"status": "failed", "message": "Routeur MikroTik introuvable."}

        wg = microtik.subscriptionwg

        try:
            with self.session() as (pool, api):
                hotspot_profile_api = api.get_resource(self.urls("hotspot_profile"))
                mikrotik_profiles = hotspot_profile_api.get()

                profiles_synced = 0

                with transaction.atomic():
                    for mk_prof in mikrotik_profiles:
                        prof_name = mk_prof.get("name")
                        if prof_name == "default":
                            continue

                        session_timeout = mk_prof.get("session-timeout", "00:00:00")
                        rate_limit = mk_prof.get("rate-limit", "")
                        shared_users = int(mk_prof.get("shared-users", 1))

                        up_rate, down_rate = (0, 0)
                        if rate_limit:
                            try:
                                up_rate, down_rate = parse_mikrotik_rate(rate_limit)
                            except ValueError:
                                logger.warning("Rate limit invalide: %s", rate_limit)

                        Profil.objects.update_or_create(
                            microtik=microtik,
                            name=prof_name,
                            defaults={
                                "rate_limit": rate_limit or "SILVER_MIN",
                                "shared_users": shared_users,
                                "session_timeout": session_timeout,
                                "up_rate": up_rate,
                                "down_rate": down_rate,
                                "price": 0.00,
                                "status": "ACTIVE",
                            },
                        )
                        profiles_synced += 1

                return {
                    "status": "success",
                    "message": f"Synchronisation réussie. {profiles_synced} profils mis à jour ou importés.",
                }

        except Exception as e:
            logger.error("sync_profils_to_db error: %s", e)
            return {"status": "failed", "message": f"Erreur synchro : {e}"}

    # ============================================================
    # 2. CLIENTS / HOTSPOT USERS
    # ============================================================
    def create_ticket_code(
        self,
        microtik: Microtik,
        code_paye: list[str],
        profile_name: str,
        limit_uptime: str,
        comment: str,
    ) -> dict:
        """
        Crée des tickets Hotspot (users) avec des codes uniques.
        """
        try:
            with self.session() as (pool, api):
                list_user = api.get_resource(self.urls("hotspot_user"))

                codes_crees = 0
                codes_existants = 0
                code_created = []

                for code in code_paye:
                    try:
                        list_user.add(
                            name=code,
                            password=code,
                            profile=profile_name,
                            limit_uptime=limit_uptime,
                            comment=comment,
                        )
                        codes_crees += 1
                        code_created.append(code)
                    except Exception as e:
                        if "already exists" in str(e).lower():
                            codes_existants += 1
                            continue
                        raise

                return {
                    "status": "success",
                    "message": (
                        f"{codes_crees} ticket(s) créé(s) avec succès. "
                        f"({codes_existants} déjà existant(s))"
                    ),
                    "codes": code_created,
                }

        except Exception as e:
            logger.error("create_ticket_code error: %s", e)
            return {"status": "failed", "message": f"Erreur génération tickets : {e}"}

    def create_client(
        self,
        microtik: Microtik,
        profil_slug: str,
        user_numbers: int,
        gdms_service=None,
    ) -> dict | list:
        """
        Crée N clients (tickets) sur le MikroTik et en BDD.
        Si device_type == GDMS, génère aussi des vouchers GDMS.
        """
        profil = microtik.profils.filter(slug=profil_slug).first()
        if not profil:
            raise HttpError(
                status_code=400,
                message="Aucun slug correspondant à ce profil.",
            )

        device_type = microtik.device_type
        subs = microtik.subscriptionwg
        tickets = None

        # --- Vouchers GDMS en parallèle si device type == GDMS
        if device_type == RouteurType.GDMS.value and gdms_service is not None:
            tickets = gdms_service.create_vouchers(
                network_id=subs.gdms_network_id,
                upRate=profil.up_rate,
                downRate=profil.down_rate,
                name=f"voucher_{profil.name}",
                count=user_numbers,
                effect_duration_map=profil.session_timeout_dict,
                max_devices=profil.shared_users,
            )

        codes = [generer_code_unique() for _ in range(user_numbers)]

        users = self.create_ticket_code(
            microtik=microtik,
            code_paye=codes,
            profile_name=profil.name,
            limit_uptime=profil.session_timeout,
            comment=f"Date: {datetime.fromtimestamp(timezone.now().timestamp())} admin generation",
        )

        if users.get("status", False) is False:
            return {
                "username": "",
                "password": "",
                "profile_name": "",
                "limit_uptime": "",
            }

        codes_created = users.get("codes", [])

        model_client = [
            Client(
                code_username=code,
                code_password=code,
                microtik=microtik,
                generate=Client.OWNER,
                limit_uptime=profil.session_timeout,
                profil_name=profil.name,
            )
            for code in codes_created
        ]
        Client.objects.bulk_create(model_client)

        return [
            {
                "username": code,
                "password": code,
                "profile_name": profil.name,
                "limit_uptime": profil.session_timeout,
            }
            for code in codes_created
        ]

    def block_unblock_client(
        self,
        microtik: Microtik,
        user_slug: str,
        is_desable: bool,
    ) -> dict:
        client = microtik.clients.filter(slug=user_slug).first()
        if not client:
            raise HttpError(
                status_code=400,
                message="Le slug de ce client n'existe pas.",
            )

        try:
            with self.session() as (pool, api):
                list_user = api.get_resource(self.urls("hotspot_user"))
                users_trouves = list_user.get(name=client.code_username)

                if not users_trouves:
                    return {
                        "status": "failled",
                        "message": "Ce client n'existe pas sur le MikroTik.",
                    }

                user_internal_id = users_trouves[0].get(
                    ".id", users_trouves[0].get("id")
                )

                if is_desable:
                    list_user.set(id=user_internal_id, disabled="yes")

                    active_resource = api.get_resource(self.urls("hotspot_active"))
                    session_active = active_resource.get(user=client.code_username)
                    if session_active:
                        act_id = session_active[0].get(
                            ".id", session_active[0].get("id")
                        )
                        active_resource.remove(id=act_id)

                    client.status = Client.DISABLE
                else:
                    list_user.set(id=user_internal_id, disabled="no")
                    client.status = Client.ACTIVE

                client.save()
                return {
                    "status": "success",
                    "message": "Modification effectuée avec succès",
                }

        except Exception as e:
            logger.error("block_unblock_client error: %s", e)
            return {"status": "failled", "message": f"Erreur : {e}"}

    def kick_client(self, microtik: Microtik, username: str) -> dict:
        """Expulse un utilisateur de la session active sans désactiver son ticket."""
        try:
            with self.session() as (pool, api):
                active_resource = api.get_resource(self.urls("hotspot_active"))
                session_active = active_resource.get(user=username)

                if session_active:
                    act_id = session_active[0].get(".id", session_active[0].get("id"))
                    active_resource.remove(id=act_id)
                    return {
                        "status": "success",
                        "message": f"L'utilisateur {username} a été déconnecté.",
                    }

                return {
                    "status": "success",
                    "message": "L'utilisateur n'avait pas de session active.",
                }

        except Exception as e:
            logger.error("kick_client error: %s", e)
            return {"status": "failled", "message": f"Erreur : {e}"}

    def reset_uptime(self, microtik: Microtik, user_slug: str) -> dict:
        """Réinitialise les compteurs (temps + octets) d'un utilisateur."""
        client = microtik.clients.filter(slug=user_slug).first()
        if not client:
            return {"status": "failled", "message": "Client introuvable."}

        try:
            with self.session() as (pool, api):
                user_resource = api.get_resource(self.urls("hotspot_user"))
                user_data = user_resource.get(name=client.code_username)

                if not user_data:
                    return {
                        "status": "failled",
                        "message": "Utilisateur introuvable sur le routeur.",
                    }

                user_id = user_data[0].get(".id", user_data[0].get("id"))
                api.get_binary_command(self.urls("hotspot_user_reset"))(id=user_id)

                client.status = Client.ACTIVE
                client.save()

                return {
                    "status": "success",
                    "message": f"Compteurs réinitialisés pour {client.code_username}.",
                }

        except Exception as e:
            logger.error("reset_uptime error: %s", e)
            return {"status": "failled", "message": f"Erreur reset : {e}"}

    def list_active_clients(self, microtik: Microtik) -> list[dict]:
        try:
            with self.session() as (pool, api):
                active_resource = api.get_resource(self.urls("hotspot_active"))
                active_users = active_resource.get()

                users_list = []
                for session in active_users:
                    try:
                        session_timeout = int(session.get("session-timeout", 0))
                        uptime = int(session.get("uptime", 0))
                        expire_in = session_timeout - uptime if session_timeout > 0 else None
                        expire_minutes = expire_in // 60 if expire_in else 0
                    except (ValueError, TypeError):
                        expire_minutes = 0

                    users_list.append(
                        {
                            "username": session.get("user", ""),
                            "ip": session.get("address", ""),
                            "connexion_time": session.get("uptime", ""),
                            "expire_in": expire_minutes,
                        }
                    )

                return users_list

        except Exception as e:
            logger.error("list_active_clients error: %s", e)
            return []

    def list_no_expired_clients(self, microtik: Microtik) -> list[dict]:
        try:
            with self.session() as (pool, api):
                user_resource = api.get_resource(self.urls("hotspot_user"))
                all_users = user_resource.get()

                user_list = []
                for user in all_users:
                    limit = user.get("limit-uptime")
                    used = user.get("uptime", "0s")

                    if limit and used != limit:
                        user_list.append(
                            {
                                "name": user.get("name"),
                                "limit_uptime": limit,
                                "uptime": used,
                                "address": user.get("address"),
                                "profile": user.get("profile"),
                                "disabled": user.get("disabled"),
                            }
                        )
                return user_list

        except Exception as e:
            logger.error("list_no_expired_clients error: %s", e)
            return []

    # ============================================================
    # 3. CONNEXION / SANTÉ
    # ============================================================
    async def check_connexion(self, microtik: Microtik) -> dict:
        """Vérifie que la connexion via WireGuard fonctionne."""
        if not self.username or not self.password:
            raise HttpError(
                status_code=400,
                message="Veuillez renseigner les informations d'utilisateur MikroTik.",
            )

        res = self.connect()
        if not res["status"]:
            return {"status": "failled", "message": res["message"]}

        try:
            return {
                "status": "success",
                "message": "Connexion établie avec succès via WireGuard.",
            }
        finally:
            try:
                res["pool"].disconnect()
            except Exception:
                pass