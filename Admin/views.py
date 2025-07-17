from django.shortcuts import render


def AdminPage(request):
    return render(request, 'admin/dashboard.html', {'page_title': 'Admin | Stock Vault'})