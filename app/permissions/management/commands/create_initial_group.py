from django.core.management.base import BaseCommand
from app.permissions.models import Permissions, PermissionGroup



class Command(BaseCommand):
    help = 'Crée les groupes de permissions par défaut'

    def handle(self, *args, **options):
        groups_data = [
            {
                "name": "Proprietaire microtik",
                "description": "Groupe des propriétaires de microtiks avec tous les droits sur leurs routeurs"
            },
            {
                "name": "Super Administration",
                "description": "Super administrateurs avec tous les droits sur toute la plateforme"
            },
            {
                "name": "Administration",
                "description": "Administrateurs avec droits de gestion des utilisateurs et des permissions"
            },
            {
                "name": "Gerant microtik",
                "description": "Gestionnaires de microtiks avec droits de gestion des profils et des clients"
            },
            {
                "name": "Partenaire",
                "description": "Partenaires avec accès limité aux microtiks et aux statistiques"
            },
            {
                "name": "Profil Manager",
                "description": "Gestion des profils Hotspot (création, modification, suppression)"
            },
            {
                "name": "Client Manager",
                "description": "Gestion des clients Hotspot (création, modification, suppression, import/export)"
            },
            {
                "name": "Finance Manager",
                "description": "Gestion des finances (retraits, dépôts, gains, commissions)"
            },
            {
                "name": "Abonnement Manager",
                "description": "Gestion des abonnements VPN WireGuard (création, renouvellement, annulation)"
            }
        ]

        group_count = 0
        created_list = []
        existing_list = []

        for group_data in groups_data:
            name = group_data.get("name", "")
            description = group_data.get("description", "") 
            
            group, created = PermissionGroup.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "is_active": True
                }
            )
            
            if created:
                group_count += 1
                created_list.append(name)
                self.stdout.write(self.style.SUCCESS(f" Groupe créé: {name}"))
            else:
                existing_list.append(name)
                self.stdout.write(self.style.WARNING(f"⏭ Groupe existe déjà: {name}"))

        self.stdout.write(self.style.SUCCESS(
            f"\n{'='*50}\n"
            f"RÉSUMÉ:\n"
            f"   • {group_count} groupe(s) créé(s) avec succès\n"
            f"   • {len(existing_list)} groupe(s) déjà existant(s)\n"
            f"\n Groupes créés: {', '.join(created_list) if created_list else 'Aucun'}\n"
            f" Groupes existants: {', '.join(existing_list) if existing_list else 'Aucun'}\n"
            f"{'='*50}"
        ))