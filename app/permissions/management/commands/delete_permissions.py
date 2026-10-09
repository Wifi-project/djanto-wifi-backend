
from django.core.management.base import BaseCommand
from app.permissions.enum_permissions import PermissionsEnum
from app.permissions.models import Permissions


class Command(BaseCommand):
    help = 'Supprime les permissions qui ne sont plus dans l\'enum'
        
    def handle(self, *args, **options):
        
        valid_codes = [p.value for p in PermissionsEnum]
        orphan_permissions = Permissions.objects.exclude(code__in=valid_codes)
        
        count = orphan_permissions.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('Aucune permission orpheline trouvée'))
            return
        
        self.stdout.write(f'Permissions orphelines trouvées: {count}')
        for perm in orphan_permissions:
            self.stdout.write(f'  - {perm.code}: {perm.name}')
            orphan_permissions.delete()

        self.stdout.write(self.style.SUCCESS(f'{count} permissions supprimées'))

