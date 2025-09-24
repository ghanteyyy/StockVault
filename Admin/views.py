import datetime
from django.shortcuts import render
import Users.models as user_models
import Shares.models as share_models
from django.http import JsonResponse
from django.db.models import CharField
from django.db.models.functions import Cast, TruncDate
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def AdminPage(request):
    table_heads = ['Name', 'Gender', "Date of Birth", "Email", "Joined At", 'Action']

    users = (user_models.CustomUser.objects
        .filter(is_active=True)
        .annotate(
            dob_str=Cast('date_of_birth', CharField()),
            joined_str=Cast(TruncDate('date_joined'), CharField()),
        )
        .values_list('name','gender','dob_str','email','joined_str')
    )

    context = {
        'users': users,
        'table_heads': table_heads,
        'page_title': 'Admin | Stock Vault',
    }

    return render(request, 'admin/users.html', context)


@login_required(login_url='login')
def EditUser(request):
    if request.method.lower() == 'post':
        dob = request.POST.get('dob', '').strip()
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        gender = request.POST.get('gender', '').strip()
        password = request.POST.get('password', '').strip()

        user = user_models.CustomUser.objects.get(email=email)

        if dob:
            user.date_of_birth = datetime.datetime.strptime(dob, '%Y-%m-%d')

        if name:
            user.name = name

        if gender:
            user.gender = gender

        if password:
            user.set_password(password)

        user.save()

        return JsonResponse({'status': True, 'message': 'User info edited successfully'})

    return JsonResponse({'status': False, 'message': 'Something went wrong'})


@login_required(login_url='login')
def AddUser(request):
    if request.method.lower() == 'post':
        dob = request.POST.get('dob', '').strip()
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        gender = request.POST.get('gender', '').strip()
        password = request.POST.get('password', '').strip()

        if user_models.CustomUser.objects.filter(email=email):
            return JsonResponse({'status': False, 'message': 'Email already exists'})

        user = user_models.CustomUser(email=email, name=name, gender=gender, date_of_birth=dob)
        user.set_password(password)
        user.save()

        return JsonResponse({'status': True, 'message': 'User added successfully'})

    return JsonResponse({'status': False, 'message': 'Something went wrong'})


@login_required(login_url='login')
def DeleteUser(request):
    try:
        email = request.GET.get('email', '')

        user = user_models.CustomUser.objects.get(email=email, is_active=True)
        user.is_active = False
        user.save()

        return JsonResponse({'status': True, 'message': 'User deleted successfully'})

    except user_models.CustomUser.DoesNotExist:
        return JsonResponse({'status': False, 'message': 'User not found'})


@login_required(login_url='login')
def AdminListedCompanies(request):
    companies = share_models.ListedCompanies.objects.all().values_list("name", "sector", "id", "abbreviation")

    table_heads = ['Symbol', 'Sector', 'Actions']

    context = {
        'companies': companies,
        'table_heads': table_heads,
        'page_title': 'Admin | Stock Vault',
    }

    return render(request, 'admin/companies.html', context)


@login_required(login_url='login')
def AdminListedCompaniesAdd(request):
    if request.method.lower() == 'post':
        company_name = request.POST.get('company_name', '').strip()
        company_sector = request.POST.get('company_sector', '').strip()
        company_abbreviation = request.POST.get('company_abbreviation', '').strip()

        if share_models.ListedCompanies.objects.filter(name=company_name):
            return JsonResponse({'status': False, 'message': 'Company already exists'})

        company = share_models.ListedCompanies(name=company_name, sector=company_sector, abbreviation=company_abbreviation)
        company.save()

        return JsonResponse({'status': True, 'message': 'Cpmpany added successfully'})

    return JsonResponse({'status': False, 'message': 'Something went wrong'})


@login_required(login_url='login')
def AdminListedCompaniesEdit(request):
    if request.method.lower() == 'post':
        company_id = request.POST.get('company_id', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        company_sector = request.POST.get('company_sector', '').strip()
        company_abbreviation = request.POST.get('company_abbreviation', '').strip()

        if not share_models.ListedCompanies.objects.filter(id=company_id):
            return JsonResponse({'status': False, 'message': 'Company does not exist'})

        company = share_models.ListedCompanies.objects.get(id=company_id)
        company.name = company_name
        company.sector = company_sector
        company.abbreviation = company_abbreviation
        company.save()

        return JsonResponse({'status': True, 'message': 'Company information updated successfully'})

    return JsonResponse({'status': False, 'message': 'Something went wrong'})


@login_required(login_url='login')
def AdminListedCompaniesDelete(request):
    company_id = request.GET.get('company_id', '').strip()

    if not share_models.ListedCompanies.objects.filter(id=company_id):
        return JsonResponse({'status': False, 'message': 'Company does not exist'})

    company = share_models.ListedCompanies.objects.get(id=company_id)
    company.delete()

    return JsonResponse({'status': True, 'message': 'Company deleted successfully'})
