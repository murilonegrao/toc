from django.db import models
from django.conf import settings

# Create your models here.

class Comment(models.Model):
    ticket = models.ForeignKey('tickets.Ticket', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    internal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    