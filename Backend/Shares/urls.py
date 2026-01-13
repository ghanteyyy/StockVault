from django.urls import path, include
from . import views


urlpatterns = [
    path('api/nepse/indices/', views.NepseIndices),
    path('api/portfolios/', views.Portfolio.as_view()),
    path('api/wishlists/', views.Wishlist.as_view()),
    path('api/companies/', views.ListedCompanies),
    path('api/faqs/', views.Faqs),
]