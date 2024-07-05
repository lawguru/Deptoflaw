from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.management import CommandError
from django.core.exceptions import ValidationError
from user.models import Email
from staff.models import StaffProfile
import getpass

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser with an email as the username'

    def handle(self, *args, **kwargs):
        email = input('Email address: ')
        first_name = input('First name: ')
        last_name = input('Last name: ')
        password = getpass.getpass('Password: ')

        if not email:
            raise CommandError('Email is required')

        try:
            email_obj, created = Email.objects.get_or_create(email=email)
        except ValidationError:
            raise CommandError('Invalid email format')

        if User.objects.filter(primary_email=email_obj).exists():
            raise CommandError('A user with this email already exists')

        user = User(
            first_name=first_name,
            last_name=last_name,
            primary_email=email_obj,
            is_staff=True,
            is_superuser=True,
            role='staff'
        )

        if password:
            user.set_password(password)
        else:
            user.set_password(User.objects.make_random_password())

        user.save()
        email_obj.user = user
        email_obj.save()
        StaffProfile.objects.create(user=user)
        self.stdout.write(self.style.SUCCESS(f'Successfully created superuser with email: {email}'))
