from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

# Create your models here.

class Attachment(models.Model):
    ticket = models.ForeignKey('tickets.Ticket', null=True, blank=True, on_delete=models.CASCADE)
    comment = models.ForeignKey('comments.Comment', null=True, blank=True, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments')
    original_name = models.CharField(max_length=255)
    size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.ticket and not self.comment:
            raise ValidationError('Attachment must be related to a ticket or a comment')
        if self.ticket and self.comment:
            raise ValidationError('Attachment cannot be related to both a ticket and a comment')
        
    #criar constraints
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(ticket__isnull=False) |
                    models.Q(comment__isnull=False)
                ),
                name='attachment_must_have_ticket_or_comment'
            )
        ]
