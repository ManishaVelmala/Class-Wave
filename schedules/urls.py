from django.urls import path
from . import views

urlpatterns = [
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('lecturer/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('list/', views.schedule_list, name='schedule_list'),
    path('calendar/', views.schedule_calendar, name='schedule_calendar'),
    path('calendar/data/', views.schedule_calendar_data, name='schedule_calendar_data'),
    path('create/', views.create_schedule, name='create_schedule'),
    path('<int:pk>/', views.schedule_detail, name='schedule_detail'),
    path('<int:pk>/edit/', views.edit_schedule, name='edit_schedule'),
    path('<int:pk>/delete/', views.delete_schedule, name='delete_schedule'),
    path('<int:schedule_id>/set-reminder/', views.set_reminder, name='set_reminder'),
]
