from django.core.management.base import BaseCommand, CommandError

from insights_manager.models import AdminAccount


class Command(BaseCommand):
    help = 'Create a platform admin account for branch insight uploads.'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='Admin email address')
        parser.add_argument('--password', required=True, help='Admin password')
        parser.add_argument('--name', default='', help='Display name')

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        password = options['password']
        name = options.get('name', '')

        if AdminAccount.objects.filter(email__iexact=email).exists():
            raise CommandError(f'Admin with email {email} already exists.')

        admin = AdminAccount(email=email, name=name, is_active=True)
        admin.set_password(password)
        admin.save()

        self.stdout.write(self.style.SUCCESS(f'Created platform admin: {email}'))
