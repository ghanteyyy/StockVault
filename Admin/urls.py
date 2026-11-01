from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('admin', RedirectView.as_view(pattern_name='admin-index', permanent=False)),
    path('admin/', views.AdminOverview, name='admin-index'),
    path('admin/users', views.AdminPage, name='admin-users'),
    path('admin/user/add', views.AddUser, name='admin-user-add'),
    path('admin/user/edit', views.EditUser, name='admin-user-edit'),
    path('admin/profile', views.UserProfile, name='admin-user-profile'),
    path('admin/user/delete', views.DeleteUser, name='admin-user-delete'),
    path('admin/user/status', views.DeleteUser, name='admin-user-status'),
    path('admin/profile/change/password', views.UserChangePassword, name='admin-user-change-password'),
    path('admin/profile/change/profile-image', views.ChangeProfile, name='admin-user-change-profile-image'),
    path('admin/companies', views.AdminListedCompanies, name='admin-companies'),
    path('admin/company/add', views.AdminListedCompaniesAdd, name='admin-company-add'),
    path('admin/company/edit', views.AdminListedCompaniesEdit, name='admin-company-edit'),
    path('admin/company/delete', views.AdminListedCompaniesDelete, name='admin-company-delete'),
    path('admin/portfolios', views.AdminPortfolios, name='admin-portfolios'),
    path('admin/transactions', views.AdminTransactions, name='admin-transactions'),
    path('admin/targets', views.AdminTargets, name='admin-targets'),
    path('admin/wishlists', views.AdminWishlists, name='admin-wishlists'),
    path('admin/faqs', views.AdminFAQs, name='admin-faqs'),
    path('admin/faq/add', views.AdminFaqAdd, name='admin-faq-add'),
    path('admin/faq/edit', views.AdminFaqEdit, name='admin-faq-edit'),
    path('admin/faq/delete', views.AdminFaqDelete, name='admin-faq-delete'),
    path('admin/activity', views.AdminActivity, name='admin-activity'),
]
