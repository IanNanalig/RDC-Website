from django.core.management.base import BaseCommand
from django.db.models import Q
from projects.models import User


class Command(BaseCommand):
    help = "Create test user accounts with specified credentials and remove old test accounts"

    def handle(self, *args, **options):
        test_users = [
            {
                "email": "edrianinfiesto@gmail.com",
                "username": "Edrian Fiesto",
                "password": "C0ntributo_acc",
                "role": "staff",
                "full_name": "Edrian Fiesto",
            },
            {
                "email": "edrianpogi612@gmail.com",
                "username": "Edrian Validator",
                "password": "Validat0r_acc",
                "role": "validator",
                "full_name": "Edrian Validator",
            },
            {
                "email": "ian095108@gmail.com",
                "username": "Ian Admin",
                "password": "ZeroNine5108_",
                "role": "admin",
                "full_name": "Ian Admin",
            },
            {
                "email": "ian0999314@gmail.com",
                "username": "Ian Contributor",
                "password": "C0ntributo_acc2",
                "role": "staff",
                "full_name": "Ian Contributor",
            },
        ]

        # Build query to exclude the test users (case-insensitive)
        exclude_query = Q()
        for user_data in test_users:
            exclude_query |= Q(email__iexact=user_data["email"])

        # Delete old accounts except the ones we want to keep
        old_users = User.objects.exclude(exclude_query)
        deleted_count = old_users.count()
        if deleted_count > 0:
            self.stdout.write(
                self.style.WARNING(f"Deleting {deleted_count} old account(s)...")
            )
            for user in old_users:
                self.stdout.write(f"  - Removed: {user.email or user.username}")
            old_users.delete()

        # Create or update test users
        created_count = 0
        updated_count = 0

        for user_data in test_users:
            email = user_data["email"]
            username = user_data["username"]
            password = user_data["password"]
            role = user_data["role"]
            full_name = user_data["full_name"]

            # Get or create user
            user, created = User.objects.get_or_create(
                email__iexact=email,
                defaults={
                    "email": email,
                    "username": username,
                    "role": role,
                    "full_name": full_name,
                    "is_active": True,
                    "must_change_password": False,
                    "is_staff": role == "admin",
                },
            )

            # Update credentials and settings
            user.set_password(password)
            user.username = username
            user.role = role
            user.full_name = full_name
            user.is_active = True
            user.must_change_password = False
            user.is_staff = role == "admin"
            user.save()

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Created: {email} ({role})"
                    )
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Updated: {email} ({role})"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSummary: {created_count} created, {updated_count} updated, {deleted_count} removed"
            )
        )

