from django.db import models
from user.models import User

# Create your models here.


class RecruiterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                null=True, blank=True, related_name='recruiter_profile')
    company_name = models.CharField(
        'Name of the Company you work at', max_length=100)
    designation = models.CharField(
        'Your Position at the Company', max_length=50)

    def save(self, *args, **kwargs):
        if not self.pk and self.user == None:
            self.user = User.objects.create(role='recruiter')
        super().save(*args, **kwargs)
        self.user.save()

    def __str__(self):
        return self.user.full_name + ' | ' + self.designation + ' at ' + self.company_name
