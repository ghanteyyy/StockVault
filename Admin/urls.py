from django.urls import path
from . import views


urlpatterns = [
    path('admin/', views.AdminPage, name='admin-index'),
    path('admin/user/add', views.AddUser, name='admin-user-add'),
    path('admin/user/edit', views.EditUser, name='admin-user-edit'),
    path('admin/user/delete', views.DeleteUser, name='admin-user-delete'),
]
