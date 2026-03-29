from django.db import models
from django.conf import settings

# Create your models here.
class NotificationLog(models.Model):
    ticket = models.ForeignKey('tickets.Ticket', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20)
    success = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Notificação {self.notification_type} - {self.user}'