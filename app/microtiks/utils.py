from enum import Enum

class PermissionGroupEnum(str, Enum):
    """Énumération des groupes de permissions par défaut"""
    
    # === RÔLES PRINCIPAUX ===
    PROPRIETAIRE_MICROTIK = "proprietaire-microtik"
    INIT_PROPRIETAIRE_MICROTIK = "init-proprietaire-microtik"
    SUPER_ADMINISTRATION = "super-administration"
    ADMINISTRATION = "administration"
    GERANT_MICROTIK = "gerant-microtik"
    PARTENAIRE = "partenaire"
    
    # === GESTION DES PROFILS ===
    PROFIL_MANAGER = "profil-manager"
    PROFIL_VIEWER = "profil-viewer"
    
    # === GESTION DES CLIENTS ===
    CLIENT_MANAGER = "client-manager"
    CLIENT_VIEWER = "client-viewer"
    CLIENT_DISCONNECTOR = "client-disconnector"
    
    # === GESTION DES FINANCES ===
    FINANCE_MANAGER = "finance-manager"
    FINANCE_VIEWER = "finance-viewer"
    WITHDRAW_APPROVER = "withdraw-approver"
    
    # === GESTION DES ABONNEMENTS ===
    ABONNEMENT_MANAGER = "abonnement-manager"
    ABONNEMENT_VIEWER = "abonnement-viewer"
    ABONNEMENT_RENEWER = "abonnement-renewer"