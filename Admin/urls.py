from django.urls import path
from . import views


urlpatterns = [
    path('admin/users', views.AdminPage, name='admin-index'),
    path('admin/user/add', views.AddUser, name='admin-user-add'),
    path('admin/user/edit', views.EditUser, name='admin-user-edit'),
    path('admin/user/delete', views.DeleteUser, name='admin-user-delete'),

    path('admin/companies', views.AdminListedCompanies, name='admin-companies'),
    path('admin/company/add', views.AdminListedCompaniesAdd, name='admin-company-add'),
    path('admin/company/edit', views.AdminListedCompaniesEdit, name='admin-company-edit'),
    path('admin/company/delete', views.AdminListedCompaniesDelete, name='admin-company-delete'),

    path('admin/portfolios', views.AdminPortfolios, name='admin-portfolios'),
]
