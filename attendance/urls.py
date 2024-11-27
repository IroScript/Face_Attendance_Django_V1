# attendance/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register_face, name='register_face'),
    path('report/', views.generate_report, name='generate_report'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('attendance/history/', views.attendance_history, name='attendance_history'),
    path('employee/list/', views.employee_list, name='employee_list'),
]