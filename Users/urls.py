from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePage, name='index'),
    path('logout/', views.Logout, name='logout'),
    path('login/', views.LoginPage, name='login'),
    path('register/', views.SignupPage, name='signup'),
    path('dashboard/', views.Dashboard, name='dashboard'),
]
