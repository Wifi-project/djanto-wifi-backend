from django.core.management.base import BaseCommand
from app.permissions.models import Permissions, PermissionGroup
from app.users.models import User



class Command(BaseCommand):
    help = 'Crée un administrateur avec toutes les permissions'


    def handle(self, *args, **options):
        
        user, created = User.objects.get_or_create(
        email="admin@djanto.com",  
        defaults={
            'first_name': "Admin",
            'last_name': "djanto",
            }
        )
        
        if created:
            user.set_password("admin@djanto")
            user.is_active = True
            user.user_type = User.OWNERSYSTEME
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Admin {user.email} créé'))
        else:
            self.stdout.write(self.style.WARNING(f'Admin {user.email} existe déjà'))
        

        group, group_created = PermissionGroup.objects.get_or_create(
            slug='super-administration',
            defaults={'description': 'Groupe avec toutes les permissions'}
        )
        
        if group_created:
            all_permissions = Permissions.objects.all()
            group.permissions.add(*all_permissions)
            self.stdout.write(self.style.SUCCESS('Groupe Administrateurs créé avec toutes les permissions'))
        

        group.users.add(user)
        self.stdout.write(self.style.SUCCESS(f'{user.email} ajouté au groupe Administrateurs'))

