import os
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from projects.models import Project, User


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class Command(BaseCommand):
    help = "Bootstrap deployed data and an admin account from environment variables."

    def add_arguments(self, parser):
        parser.add_argument(
            "--load-fixture",
            action="store_true",
            help="Load the fixture configured by BOOTSTRAP_FIXTURE, default sqlite_export.json.",
        )
        parser.add_argument(
            "--force-load",
            action="store_true",
            help="Load the fixture even when projects already exist.",
        )
        parser.add_argument(
            "--make-public",
            action="store_true",
            help="Mark all projects as public dashboard visible.",
        )

    def handle(self, *args, **options):
        load_fixture = options["load_fixture"] or env_bool("BOOTSTRAP_LOAD_FIXTURE")
        force_load = options["force_load"] or env_bool("BOOTSTRAP_FORCE_LOAD")
        make_public = options["make_public"] or env_bool("BOOTSTRAP_MAKE_PUBLIC")

        if load_fixture:
            self.load_fixture(force_load=force_load)

        self.create_or_update_admin()

        if make_public:
            updated = Project.objects.update(
                validated=True,
                archived=False,
                is_active=True,
            )
            self.stdout.write(
                self.style.SUCCESS(f"Marked {updated} project(s) as public.")
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Bootstrap complete. Users: {User.objects.count()}, projects: {Project.objects.count()}"
            )
        )

    def load_fixture(self, force_load: bool):
        existing_projects = Project.objects.exists()
        if existing_projects and not force_load:
            self.stdout.write(
                self.style.WARNING(
                    "Skipping fixture load because projects already exist. Set BOOTSTRAP_FORCE_LOAD=true to override."
                )
            )
            return

        fixture_name = os.environ.get("BOOTSTRAP_FIXTURE", "sqlite_export.json")
        fixture_path = Path(settings.BASE_DIR) / fixture_name
        if not fixture_path.exists():
            raise CommandError(f"Fixture not found: {fixture_path}")

        call_command("loaddata", str(fixture_path), verbosity=1)
        self.stdout.write(self.style.SUCCESS(f"Loaded fixture: {fixture_path.name}"))

    def create_or_update_admin(self):
        email = os.environ.get("ADMIN_EMAIL") or os.environ.get("DJANGO_SUPERUSER_EMAIL")
        username = (
            os.environ.get("ADMIN_USERNAME")
            or os.environ.get("DJANGO_SUPERUSER_USERNAME")
            or email
        )
        password = os.environ.get("ADMIN_PASSWORD") or os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not email or not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Skipping admin setup. Set ADMIN_EMAIL, ADMIN_USERNAME, and ADMIN_PASSWORD."
                )
            )
            return

        user = (
            User.objects.filter(email__iexact=email).first()
            or User.objects.filter(username=username).first()
        )
        created = user is None
        if created:
            user = User(username=username, email=email)

        user.username = username
        user.email = email
        user.role = "admin"
        user.full_name = os.environ.get("ADMIN_FULL_NAME", user.full_name or username)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.must_change_password = False
        user.set_password(password)
        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} admin account: {email}"))
