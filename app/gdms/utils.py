from enum import Enum


class PermissionGroupEnum(str, Enum):
    """Énumération des groupes de permissions par défaut"""

    # === RÔLES PRINCIPAUX ===
    PROPRIETAIRE_NETWORK = "proprietaire-network"
    INIT_PROPRIETAIRE_NETWORK = "init-proprietaire-network"
    SUPER_ADMINISTRATION = "super-administration"
    ADMINISTRATION = "administration"
    GERANT_NETWORK = "gerant-network"
    PARTENAIRE = "partenaire"

    # === GESTION DES PROFILS ===
    PROFIL_MANAGER = "profil-manager"

    # === GESTION DES CLIENTS ===
    CLIENT_MANAGER = "client-manager"

    # === GESTION DES FINANCES ===
    FINANCE_MANAGER = "finance-manager"

    # === GESTION DES ABONNEMENTS ===
    ABONNEMENT_MANAGER = "abonnement-manager"