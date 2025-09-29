from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import captcha

urlpatterns = [
    path('', views.HomePage, name='index'),
    path('logout/', views.Logout, name='logout'),
    path('login/', views.LoginPage, name='login'),
    path('target/', views.TargetPage, name='target'),
    path('register/', views.SignupPage, name='signup'),
    path('predict/', views.PredictPage, name='predict'),
    path('dashboard/', views.Dashboard, name='dashboard'),
    path('portfolio/', views.Portfolio, name='portfolio'),
    path('wishlist/', views.WishListPage, name='wishlist'),
    path('settings/', views.SettingsPage, name='settings'),
    path('target/edit', views.TargetEdit, name='edit-target'),
    path('testonomials/', views.TestonomialsPage, name='testonomials'),
    path('portfolio/graph', views.PortfolioGraph, name='portfolio-graph'),
    path('verify-captcha/', captcha.VerifyCaptcha, name='verify-captcha'),
    path('trade-calculator/', views.TradeCalculator, name='trade-calculator'),
    path('generate-captcha/', captcha.GenerateCaptcha, name='generate-captcha'),
    path('target/<str:company>/delete', views.TargetDelete, name='delete-target'),
    path('predict/company/data', views.FetchCompanyPredictionData, name='predict-company-data'),
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
