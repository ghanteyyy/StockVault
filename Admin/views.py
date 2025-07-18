from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def AdminPage(request):
    return render(request, 'admin/dashboard.html', {'page_title': 'Admin | Stock Vault'})
