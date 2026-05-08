from django.urls import path
from . import views


app_name = 'attachments'

urlpatterns = [
    path('ticket/<int:ticket_id>/upload/', views.upload_attachment, name='upload'),
    path('<int:attachment_id>/download/', views.download_attachment, name='download'),
    path('<int:attachment_id>/preview/', views.preview_attachment, name='preview'),
]
