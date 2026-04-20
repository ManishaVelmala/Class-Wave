from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('notifications/unread-count/', views.unread_count, name='unread_count'),
    path('digest-preferences/', views.digest_preferences, name='digest_preferences'),
    path('generate-digest/', views.generate_my_digest, name='generate_my_digest'),
]
