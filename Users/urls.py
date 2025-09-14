from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePage, name='index'),
    path('logout/', views.Logout, name='logout'),
    path('login/', views.LoginPage, name='login'),
    path('target/', views.TargetPage, name='target'),
    path('register/', views.SignupPage, name='signup'),
    path('dashboard/', views.Dashboard, name='dashboard'),
    path('portfolio/', views.Portfolio, name='portfolio'),
    path('wishlist/', views.WishListPage, name='wishlist'),
    path('settings/', views.SettingsPage, name='settings'),
    path('target/edit', views.TargetEdit, name='edit-target'),
    path('portfolio/graph', views.PortfolioGraph, name='portfolio-graph'),
    path('trade-calculator/', views.TradeCalculator, name='trade-calculator'),
    path('target/<str:company>/delete', views.TargetDelete, name='delete-target'),
]
