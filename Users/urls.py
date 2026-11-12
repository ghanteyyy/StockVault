from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import captcha
from . import market_views
from . import notification_views
from . import trading_views

urlpatterns = [
    path('', views.HomePage, name='index'),
    path('logout/', views.Logout, name='logout'),
    path('login/', views.LoginPage, name='login'),
    path('target/', views.LegacyTargetRedirect, name='target'),
    path('register/', views.SignupPage, name='signup'),
    path('portfolio/', views.Portfolio, name='portfolio'),
    path('trades/', trading_views.TradePage, name='trades'),
    path('transactions/', trading_views.TransactionHistory, name='transactions'),
    path('wishlist/', views.WishListPage, name='wishlist'),
    path('wishlist/targets/', views.TargetCreate, name='create-target'),
    path('wishlist/targets/edit/', views.TargetEdit, name='edit-target'),
    path('wishlist/targets/<str:company>/delete/', views.TargetDelete, name='delete-target'),
    path('settings/', views.SettingsPage, name='settings'),
    path('dashboard/', views.DashboardPage, name='dashboard'),
    path('market-data/', market_views.MarketDataPage, name='market-data'),
    path('notifications/', notification_views.notification_feed, name='notification-feed'),
    path('notifications/read/', notification_views.mark_notifications_read, name='notification-read'),
    path('testonomials/', views.TestonomialsPage, name='testonomials'),
    path('portfolio/delete/', views.DeleteProtfolio, name='portfolio-delete'),
    path('verify-captcha/', captcha.VerifyCaptcha, name='verify-captcha'),
    path('trade-calculator/', views.TradeCalculator, name='trade-calculator'),
    path('generate-captcha/', captcha.GenerateCaptcha, name='generate-captcha'),
    path(
        'reset_password/',
        auth_views.PasswordResetView.as_view(
            template_name='reset_password/find_account.html',
            extra_context={'page_title': 'Reset Password | StockVault'},
            subject_template_name='registration/password_reset_subject.txt',
            email_template_name='registration/password_reset_email.txt',
            html_email_template_name='registration/password_reset_email.html'
        ),
        name='reset_password'
    ),
    path(
        'reset_password_sent/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='reset_password/reset_password_sent.html',
            extra_context={'page_title': 'Password Reset Sent | StockVault'}
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='reset_password/new_password.html',
            extra_context={'page_title': 'Enter New Password | StockVault'}
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset_password_complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='reset_password/recover_password_complete.html',
            extra_context={'page_title': 'Password Reset Complete | StockVault'}
        ),
        name='password_reset_complete'
    ),
]
