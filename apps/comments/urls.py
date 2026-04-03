from django.urls import path
from . import views


app_name = 'comments'

urlpatterns = [
    path('ticket/<int:ticket_id>/add/', views.add_comment, name='add'),
]
