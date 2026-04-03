from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('', views.ticket_list, name='list'),
    path('all/', views.ticket_list, name='list_all'),
    path('create/', views.ticket_create, name='create'),
    path('<int:ticket_id>/', views.ticket_detail, name='detail'),
    path('<int:ticket_id>/status/', views.ticket_change_status, name='change_status'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('kanban/', views.ticket_kanban, name='kanban'),
    path('<int:ticket_id>/kanban-move/', views.kanban_move_ticket, name='kanban_move'),
]
