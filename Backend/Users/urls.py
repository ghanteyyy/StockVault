from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import captcha

urlpatterns = [
    path('api/me/', views.me),
    path('api/targets/', views.Targets.as_view()),
]
