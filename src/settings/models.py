from django.db import models

# Create your models here.
class Setting(models.Model):
    key = models.CharField(max_length=50, primary_key=True)
    value = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return '[' + self.key + ', ' + self.value + ']'