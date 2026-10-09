from django.core.management.base import BaseCommand
from app.permissions.models import Permissions, PermissionGroup
from app.permissions.enum_permissions import PermissionsEnum


class Command(BaseCommand):
    help = 'Synchronise les permissions depuis l\'enum vers la base de données'
        
        
    def handle(self, *args, **options):
        
        ajout: int = 0
        for permission in PermissionsEnum:
            name = permission.name.replace('_', " ").title()
            code = permission.value
            description = permission.get_description(code)

            if not Permissions.objects.filter(code=code).exists() and not Permissions.objects.filter(name=name).exists():
                Permissions.objects.create(name=name, code=code,description=description)
                ajout += 1 
            else:
                ...
                # self.stdout.write(f"################################\n" \
                # "la permission du nom : {name} \n et du code {code} n'as pas ete enregistrer.")

        admin_group = PermissionGroup.objects.filter(name='Administration').first()
        if admin_group:
            admin_perm = admin_group.permissions.values_list('code', flat=True)
            new_perms = list(Permissions.objects.exclude(code__in=admin_perm))

            if new_perms:
                admin_group.permissions.add(*new_perms)


        self.stdout.write(self.style.SUCCESS(
            f"\n###########################################\n"
            f"{ajout} permission(s) ajoutée(s) avec succès\n"
            "Nouvelles permissions ajoutées au groupe Administration."
        ))





