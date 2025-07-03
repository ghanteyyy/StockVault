from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePage, name='index'),
    path('logout/', views.Logout, name='logout'),
    path('login/', views.LoginPage, name='login'),
    path('register/', views.SignupPage, name='signup'),
    path('dashboard/', views.Dashboard, name='dashboard'),
    path('portfolio/', views.Portfolio, name='portfolio'),
    path('wishlist/', views.WishListPage, name='wishlist'),
    path('settings/', views.SettingsPage, name='settings'),
    path('profit-loss/', views.ProfitLossPage, name='profit-loss'),
    path('portfolio/timeline/<str:company_name>', views.Timeline, name='timeline'),
]
