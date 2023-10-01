from django.core.management.base import BaseCommand
from apps.common.models import Role


class Command(BaseCommand):
    """
    Role Initializer 코드입니다.

    다음 명령어로 실행할 수 있습니다:
        python manage.py init_roles
    """

    def handle(self, *args, **options):
        roles = ["ROLE_GUEST", "ROLE_USER0", "ROLE_USER1", "ROLE_ADMIN", "ROLE_DEV"]

        for role in roles:
            Role.objects.get_or_create(name=role)

        self.stdout.write(self.style.SUCCESS("Roles initialized successfully."))
