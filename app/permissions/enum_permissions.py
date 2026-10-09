from enum import Enum


class PermissionsEnum(str, Enum):
    HEALTH_CHECK = "health_check"

    # ==========================================
    # 1. MODÈLES EXISTANTS EN BDD
    # ==========================================

    # --- Users ---
    USER_CREATE = "users:create"
    USER_READ = "users:read"
    USER_UPDATE = "users:update"
    USER_DELETE = "users:delete"
    USER_VALIDATE = "users:validate"
    USER_READ_ALL_USERS = "users:read_all_users"

    # --- Permissions & Groupes ---
    PERMISSION_READ = "permission:read"
    PERMISSION_UPDATE = "permission:update"
    PERMISSION_DELETE = "permission:delete"
    PERMISSION_CREATE = "permission:create"

    PERMISSION_GROUP_CREATE = "permission_group:create"
    PERMISSION_GROUP_READ = "permission_group:read"
    PERMISSION_GROUP_UPDATE = "permission_group:update"
    PERMISSION_GROUP_DELETE = "permission_group:delete"

    # --- Address ---
    ADDRESS_READ = "address:read"
    ADDRESS_UPDATE = "address:update"

    # --- Owner Microtik ---
    OWNER_MICROTIK_CREATE = "owner_microtik:create"
    OWNER_MICROTIK_READ = "owner_microtik:read"
    OWNER_MICROTIK_UPDATE = "owner_microtik:update"
    OWNER_MICROTIK_DELETE = "owner_microtik:delete"

    # --- Microtik (Routeurs) ---
    MICROTIK_CREATE = "microtik:create"
    MICROTIK_READ = "microtik:read"
    MICROTIK_UPDATE = "microtik:update"
    MICROTIK_DELETE = "microtik:delete"
    MICROTIK_BLOCK = "microtik:block"
    MICROTIK_UNBLOCK = "microtik:unblock"
    MICROTIK_ADD_OWNER = "microtik:add_owner"
    MICROTIK_REMOVE_OWNER = "microtik:remove_owner"
    MICROTIK_CREATE_OWNER = "microtik:create_owner"
    MICROTIK_ADD_PERMISSIONS = "microtik:add_permissions"
    MICROTIK_REMOVE_PERMISSIONS = "microtik:remove_permissions"
    MICROTIK_SYNC = "microtik:sync"

    # --- Profils (Hotspot Profiles) ---
    PROFIL_CREATE = "profil:create"
    PROFIL_READ = "profil:read"
    PROFIL_UPDATE = "profil:update"
    PROFIL_DELETE = "profil:delete"
    PROFIL_SYNC = "profil:sync"

    # --- Finance & Retraits (Windraw / Gains) ---
    FINANCE_READ_SUMMARY = "finance:read_summary"
    FINANCE_REQUEST_WITHDRAW = "finance:request_withdraw"
    FINANCE_READ_WITHDRAW = "finance:read_withdraw"
    FINANCE_READ_ALL_WITHDRAW = "finance:read_all_withdraw"
    FINANCE_APPROVE_WITHDRAW = "finance:approve_withdraw"
    FINANCE_REJECT_WITHDRAW = "finance:reject_withdraw"
    FINANCE_CANCEL_WITHDRAW = "finance:cancel_withdraw"

    GAIN_SYSTEME_READ = "gain_systeme:read"
    GAIN_SYSTEME_READ_ALL = "gain_systeme:read_all"


    # ==========================================
    # 2. PERMISSIONS AJOUTÉES (Non présentes dans la première version)
    # ==========================================

    # --- Abonnements WireGuard / VPN (Pointeurs subscriptionwg de ton modèle Microtik) ---
    SUBSCRIPTION_READ = "subscription:read"
    SUBSCRIPTION_CREATE = "subscription:create"
    SUBSCRIPTION_RENEW = "subscription:renew"
    SUBSCRIPTION_CANCEL = "subscription:cancel"
    SUBSCRIPTION_READ_ALL = "subscription:read_all"
    SUBSCRIPTION_UPDATE = "subscription:update"
    SUBSCRIPTION_CONFIGURATION= "subscription:configuration"

    # --- Dépôts & Paiements (InfoDeposit / Webhooks d'opérateurs) ---
    DEPOSIT_READ = "deposit:read"
    DEPOSIT_READ_ALL = "deposit:read_all"
    DEPOSIT_RETRY = "deposit:retry"
    DEPOSIT_CANCEL = "deposit:cancel"

    # --- Tickets / Clients Hotspot (Modèle Client généré après paiement) ---
    CLIENT_READ = "client:read"
    CLIENT_GROUP = "client:read_group"
    CLIENT_CREATE = "client:create"
    CLIENT_DELETE = "client:delete"
    CLIENT_DISCONNECT = "client:disconnect"  # Déconnecter un utilisateur actif du MikroTik
    CLIENT_BLOCKED = "client:blocked"  # bloquer un client
    CLIENT_UNBLOCKED = "client:unblocked"  # deverrouiller un client

    #--- Prix de Base (BasePrice) ---
    BASE_PRICE_READ = "base_price:read"
    BASE_PRICE_CREATE = "base_price:create"
    BASE_PRICE_UPDATE = "base_price:update"
    BASE_PRICE_DELETE = "base_price:delete"
    BASE_PRICE_READ_ALL = "base_price:read_all"

    # --- Gestion des catégories d'abonnement ---
    CATEGORY_READ = "category:read"
    CATEGORY_CREATE = "category:create"
    CATEGORY_UPDATE = "category:update"
    CATEGORY_DELETE = "category:delete"
    CATEGORY_READ_ALL = "category:read_all"

    # --- Monitoring & Métriques Routeurs (Ping, Vitesse, Uptime, IP) ---
    MONITORING_READ = "monitoring:read"
    MONITORING_READ_ALL = "monitoring:read_all"

    # --- Journaux d'Audit & Activity Logs (Traçabilité des actions) ---
    AUDIT_LOG_READ = "audit_log:read"
    AUDIT_LOG_READ_ALL = "audit_log:read_all"

    # --- Configuration Système & Webhooks ---
    SYSTEM_CONFIG_READ = "system_config:read"
    SYSTEM_CONFIG_UPDATE = "system_config:update"
    WEBHOOK_MANAGE = "webhook:manage"


    @classmethod
    def get_description(cls, code: str) -> str:
        descriptions = {
            "health_check": "Permet de vérifier l'état du service",

            # Users
            "users:create": "Création d'un utilisateur",
            "users:read": "Lecture des utilisateurs",
            "users:update": "Mise à jour des utilisateurs",
            "users:delete": "Suppression des utilisateurs",
            "users:validate": "Validation des utilisateurs",
            "users:read_all_users": "La lecture de tous les utilisateurs",

            # Permissions & Groupes
            "permission:read": "Lecture des permissions",
            "permission:update": "Mise à jour des permissions",
            "permission:delete": "La suppression des permissions",
            "permission:create": "La création des permissions",

            "permission_group:create": "Création d'un groupe de permissions",
            "permission_group:read": "Lecture des groupes de permissions",
            "permission_group:update": "Mise à jour des groupes de permissions",
            "permission_group:delete": "Suppression des groupes de permissions",

            # Address
            "address:read": "La lecture des adresses",
            "address:update": "Mise à jour des adresses",

            # Owner Microtik
            "owner_microtik:create": "Création d'un propriétaire MikroTik",
            "owner_microtik:read": "Lecture des détails d'un propriétaire MikroTik",
            "owner_microtik:update": "Mise à jour d'un propriétaire MikroTik",
            "owner_microtik:delete": "Suppression d'un propriétaire MikroTik",

            # Microtik
            "microtik:create": "Ajout d'un nouveau routeur MikroTik",
            "microtik:read": "Lecture de la liste et des détails des routeurs MikroTik",
            "microtik:update": "Mise à jour des configurations du routeur MikroTik",
            "microtik:delete": "Suppression d'un routeur MikroTik",
            "microtik:block": "Blocage administratif d'un routeur MikroTik",
            "microtik:add_owner": "ajouter un admin pour le microtik",
            "microtik:remove_owner": "retirer le admin",
            "microtik:create_owner": "cree un compte admin",
            "microtik:add_permissions": "ajouter une permission a un admin",
            "microtik:remove_permissions": "retirer une permission a un admin",
            "microtik:unblock": "Déblocage d'un routeur MikroTik",
            "microtik:sync": "Synchronisation manuelle avec le routeur MikroTik",

            # Profils
            "profil:create": "Création d'un profil tarifaire Hotspot",
            "profil:read": "Lecture des profils Hotspot",
            "profil:update": "Mise à jour des tarifs et vitesses d'un profil",
            "profil:delete": "Suppression d'un profil Hotspot",
            "profil:sync": "Synchronisation des profils avec le MikroTik",

            # Finance
            "finance:read_summary": "Consulter le résumé financier (solde, gains, statistiques)",
            "finance:request_withdraw": "Demander un retrait de solde (Mobile Money/Banque)",
            "finance:read_withdraw": "Consulter ses propres demandes de retrait",
            "finance:read_all_withdraw": "Consulter toutes les demandes de retrait (Admin)",
            "finance:approve_withdraw": "Approuver et valider un paiement de retrait",
            "finance:reject_withdraw": "Rejeter une demande de retrait",
            "finance:cancel_withdraw": "Annuler sa propre demande de retrait en attente",

            # Base Price
            "base_price:read": "Consulter les prix de base des profils",
            "base_price:create": "Créer un nouveau prix de base pour un profil",
            "base_price:update": "Modifier un prix de base existant",
            "base_price:delete": "Supprimer un prix de base",
            "base_price:read_all": "Consulter tous les prix de base (Admin)",

            # Gain Système
            "gain_systeme:read": "Consulter les commissions prélevées pour ses routeurs",
            "gain_systeme:read_all": "Consulter la totalité des gains plateforme (Super Admin)",


            # ==========================================
            # CATÉGORIES D'ABONNEMENT
            # ==========================================
            "category:read": "Consulter les catégories d'abonnement VPN",
            "category:create": "Créer une nouvelle catégorie d'abonnement VPN",
            "category:update": "Modifier une catégorie d'abonnement VPN existante",
            "category:delete": "Supprimer une catégorie d'abonnement VPN",
            "category:read_all": "Consulter toutes les catégories d'abonnement (Admin)",

            # --- DESCRIPTIONS DES NOUVELLES PERMISSIONS AJOUTÉES ---
            # Abonnements WireGuard / Tunnel VPN
            "subscription:read": "Consulter le statut de l'abonnement VPN WireGuard du routeur",
            "subscription:create": "Créer un abonnement VPN WireGuard pour un routeur",
            "subscription:renew": "Renouveler un abonnement WireGuard expiré",
            "subscription:cancel": "Résilier un abonnement WireGuard",
            "subscription:read_all": "Voir la totalité des abonnements VPN actifs (Admin)",
            "subscription:update": "mettre a jour les access du routeur",
            "subscription:configuration": "payer les frais de configuration",

            # Dépôts & Paiements
            "deposit:read": "Consulter l'historique de ses ventes et dépôts",
            "deposit:read_all": "Consulter toutes les transactions du système",
            "deposit:retry": "Relancer manuellement la génération d'un ticket bloqué",
            "deposit:cancel": "Annuler ou invalider un dépôt de paiement",

            # Clients & Tickets Hotspot
            "client:read": "Consulter la liste des tickets/codes générés",
            "client:create": "Générer manuellement un ticket/code utilisateur",
            "client:delete": "Supprimer un ticket/code d'accès",
            "client:disconnect": "Déconnecter de force un client du réseau Wi-Fi",
            "client:blocked": "Bloquer un client sur le routeur MikroTik",
            "client:unblocked": "Débloquer un client sur le routeur MikroTik",
            "client:read_group": "lire les groupe de client.",

            # Monitoring
            "monitoring:read": "Voir les métriques en direct (CPU, RAM, état en ligne, clients connectés)",
            "monitoring:read_all": "Voir le tableau de bord de supervision de tous les routeurs",

            # Audit & Journaux
            "audit_log:read": "Consulter l'historique de ses actions et connexions",
            "audit_log:read_all": "Consulter tous les journaux d'audit du système (Admin)",

            # Configuration & Webhooks
            "system_config:read": "Consulter les paramètres globaux de la plateforme",
            "system_config:update": "Modifier les configurations systèmes de la plateforme",
            "webhook:manage": "Gérer et rejouer les notifications webhooks d'opérateurs",
        }
        return descriptions.get(code, code.replace(':', ' ').replace('_', ' ').title())