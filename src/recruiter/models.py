from django.db import models

# Create your models here.


class RecruiterProfile(models.Model):
    user = models.OneToOneField('user.User', on_delete=models.CASCADE, null=True, blank=True, related_name='recruiter_profile')
    company_name = models.CharField('Name of the Company you work at', max_length=100)
    designation = models.CharField('Your Position at the Company', max_length=50)

    def __str__(self):
        return self.company_name