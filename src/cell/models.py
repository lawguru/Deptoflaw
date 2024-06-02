from django.db import models
from django.db.models.functions import Lower
from user.models import User

# Create your models here.


class Notice(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True, editable=False)
    date_edited = models.DateTimeField(auto_now=True, editable=False)
    added_by = models.ForeignKey(
        'user.User', null=True, on_delete=models.SET_NULL, related_name='notices')

    def __str__(self):
        return self.title


class Message(models.Model):
    sender = models.CharField(max_length=150)
    sender_designation = models.CharField(max_length=150)
    sender_company = models.CharField(max_length=150)
    sender_phone = models.CharField(max_length=150)
    sender_email = models.EmailField()
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True, editable=False)
    date_edited = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.sender


class Quote(models.Model):
    quote = models.TextField()
    author = models.CharField(max_length=150)
    source = models.CharField(max_length=150, blank=True, null=True)
    fictional = models.BooleanField(default=False)

    def __str__(self):
        return self.quote + ' - ' + self.author

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('quote'),
                name='unique_quote'
            ),
        ]
        ordering = ['author']