from django.urls import path
from . import views


urlpatterns = [
    path('admin/users', views.AdminPage, name='admin-index'),
    path('admin/user/add', views.AddUser, name='admin-user-add'),
    path('admin/user/edit', views.EditUser, name='admin-user-edit'),
    path('admin/profile', views.UserProfile, name='admin-user-profile'),
    path('admin/user/delete', views.DeleteUser, name='admin-user-delete'),
    path('admin/profile/change/password', views.UserChangePassword, name='admin-user-change-password'),
    path('admin/profile/change/profile-image', views.ChangeProfile, name='admin-user-change-profile-image'),

    path('admin/companies', views.AdminListedCompanies, name='admin-companies'),
    path('admin/company/add', views.AdminListedCompaniesAdd, name='admin-company-add'),
    path('admin/company/edit', views.AdminListedCompaniesEdit, name='admin-company-edit'),
    path('admin/company/delete', views.AdminListedCompaniesDelete, name='admin-company-delete'),

    path('admin/portfolios', views.AdminPortfolios, name='admin-portfolios'),
    path('admin/portfolioLots', views.AdminPortfoliosLots, name='admin-portfolioLots'),
    path('admin/transactions', views.AdminTransactions, name='admin-transactions'),
    path('admin/targets', views.AdminTargets, name='admin-targets'),
    path('admin/wishlists', views.AdminWishlists, name='admin-wishlists'),

    path('admin/faqs', views.AdminFAQs, name='admin-faqs'),
    path('admin/faq/add', views.AdminFaqAdd, name='admin-faq-add'),
    path('admin/faq/edit', views.AdminFaqEdit, name='admin-faq-edit'),
    path('admin/faq/delete', views.AdminFaqDelete, name='admin-faq-delete'),

    path('admin/market/data', views.AdminMarketData, name='admin-market-data'),
    path('api/stockmarketdata/', views.stockmarketdata_dt, name='stockmarketdata_dt'),
]
