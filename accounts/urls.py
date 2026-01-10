from django.urls import path, include
from . import views


urlpatterns = [
    path('api/captcha/generate/', views.get_captcha),
    path('api/captcha/verify/', views.verify_captcha),
    path('api/auth/login/', views.Login),
    path('api/auth/logout/', views.Logout),
]