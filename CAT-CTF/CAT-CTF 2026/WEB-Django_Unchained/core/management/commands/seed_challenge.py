from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from pathlib import Path


class Command(BaseCommand):
    help = "Prepare challenge runtime data."

    def handle(self, *args, **options):
        password = self._admin_password()
        reviewer, _ = User.objects.update_or_create(
            username=settings.ADMIN_USERNAME,
            defaults={"email": "reviewer@cat26.local", "is_staff": True, "is_superuser": True},
        )
        reviewer.set_password(password)
        reviewer.save()

        self.stdout.write(self.style.SUCCESS("challenge data ready"))

    def _admin_password(self):
        if settings.ADMIN_PASSWORD:
            return settings.ADMIN_PASSWORD
        path = Path(settings.ADMIN_PASSWORD_FILE)
        if path.exists():
            return path.read_text().strip()
        path.parent.mkdir(parents=True, exist_ok=True)
        password = get_random_string(48)
        path.write_text(password)
        return password
