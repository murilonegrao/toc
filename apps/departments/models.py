from django.db import models

# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=100, null=False)
    initials = models.CharField(max_length=10, unique=True, null=False)
    active = models.BooleanField(default=True)
    color = models.CharField(max_length=7, default='#4A90D9')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.initials