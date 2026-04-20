from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('schedules/', include('schedules.urls')),
    path('reminders/', include('reminders.urls')),
]
