from django.db import models
from django.db.models import Q
from user.models import User

# Create your models here.


class RecruiterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                null=True, blank=True, related_name='recruiter_profile')
    company_name = models.CharField(
        'Name of the Company you work at', max_length=100)
    designation = models.CharField(
        'Your Position at the Company', max_length=50)

    @cached_property
    def edit_users(self):
        return self.user.edit_users

    @cached_property
    def view_users(self):
        return self.user.view_users

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.user.save()

    def __str__(self):
        return self.user.full_name + ' | ' + self.designation + ' at ' + self.company_name
