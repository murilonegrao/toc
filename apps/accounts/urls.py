from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('pending/', views.pending_approval, name='pending'),
    path('select-department/', views.select_department, name='select_department'),
    path('pending-users/', views.pending_users, name='pending_users'),
    path('approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('reject/<int:user_id>/', views.reject_user, name='reject_user'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
]