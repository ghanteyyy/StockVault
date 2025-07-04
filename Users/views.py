import re
import json
import collections
import datetime as dt
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
import Shares.views as share_views
import Users.models as user_models
import Shares.models as share_models
import Shares.serializers as share_serializers


def HomePage(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    return render(request, 'index.html', {'page_title': 'Stock Vault – Smarter Stock Tracking'})


def LoginPage(request):
    next_url = request.POST.get('next', request.GET.get('next', 'dashboard'))

    if request.method.lower() == 'post':
        email = request.POST.get('email').strip()
        password = request.POST.get('password').strip()

        try:
            validate_email(email)

            user = authenticate(request, email=email, password=password)

            if not user:
                messages.error(request, 'Credentials not matched')
                return redirect('login')

            login(request, user)
            return redirect(next_url)

        except ValidationError:
            messages.error(request, 'Invalid email address')

    return render(request, 'login.html', {'page_title': 'Stock Vault | Login', 'next': next_url})


def SignupPage(request):
    errors = []

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        gender = request.POST.get('gender').strip()
        name = request.POST.get('fullName').strip()
        password = request.POST.get('password').strip()
        profile = request.FILES['profilePicture']
        dob = request.POST.get('dob').strip()

        # Validating email
        try:
            validate_email(email)

            if user_models.CustomUser.objects.filter(email=email).exists():
                errors.append('Email already exists')

        except ValidationError:
            errors.append('Invalid email address')

        # Validating genders
        valid_genders = ['male', 'female', 'others']

        if gender not in valid_genders:
            errors.append('Invalid gender selected')

        # Validating name
        if not name and len(name) < 3:
            errors.append('Name must be at least 3 characters long')

        # Validating password
        password_regex = r'^(?=.*[A-Z])(?=.*[!@#$%^&*])(?=.*[0-9]).{8,}$'

        if not re.match(password_regex, password):
            errors.append('Password must be at least 8 characters long, contain at least one uppercase letter, one number, and one special character.')

        # Validating profile picture
        if not profile:
            errors.append('Profile picture is required')

        if profile.size == 0:
            errors.append('Profile picture cannot be empty')

        profile_size = 5 * 1024 * 1024  # 5MB limit

        if profile.size > profile_size:
            errors.append('Profile picture size must be less than 5MB')

        if not profile.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            errors.append('Only JPG/PNG images are allowed.')

        # Validating date of birth
        try:
            dob_obj = dt.datetime.strptime(dob, '%Y/%m/%d')

            today = dt.datetime.today()

            if ((today - dob_obj).days) // 365 < 13:
                errors.append('You must be at least 13 years old to register.')

        except (ValueError, TypeError) as e:
            errors.append('Invalid date of birth format. Use YYYY/MM/DD.')

        if not errors:
            new_user = user_models.CustomUser(
                email=email,
                name=name,
                gender=gender,
                date_of_birth=dob_obj.date()
            )

            new_user.profile_image = profile
            new_user.set_password(password)
            new_user.save()

            return LoginPage(request)

    return render(request, 'signup.html', {'page_title': 'Stock Vault | Register', 'errors': errors})


def Logout(request):
    logout(request)

    return redirect('index')


@login_required(login_url='login')
def Dashboard(request):
    total_stocks = 0
    portfolio_data = []
    portfolio_values = 0
    previous_portfolio_values = 0

    share_holdings = share_models.ShareHoldings.objects.filter(user_id=request.user).order_by('company_id__name').distinct('company_id__name')

    for index, share_holding in enumerate(share_holdings):
        total_stocks += share_holding.quantity

        historical_prices = share_models.HistoricalPrices.objects.filter(company_id=share_holding.company_id)

        previous_closing_price = historical_prices.last().closing_price
        previous_opening_price = historical_prices.order_by('-recorded_at')[1].closing_price

        previous_portfolio_values += share_holding.quantity * previous_opening_price
        portfolio_values += share_holding.quantity * previous_closing_price

        portfolio_data.append(
            {
                'company_name': f'{share_holding.company_id.name} ({share_holding.company_id.abbreviation})',
                'today_opening_price': previous_opening_price,
                'today_closing_price': previous_closing_price,
                'percentage_change': f"{round(((previous_closing_price - previous_opening_price) / previous_closing_price) * 100, 2)}%"
            }
        )

    if portfolio_values == 0:
        overall_gain_loss = 0

    else:
        overall_gain_loss = round(((portfolio_values - previous_portfolio_values) / portfolio_values) * 100, 2)

    recent_activites = share_models.RecentActivities.objects.filter(user_id=request.user).order_by('-recorded_at')
    recent_activites = share_serializers.RecentActivitiesSerializer(recent_activites, many=True).data[:5]

    context = {
            'page_title': 'Dashboard | Stock Vault',
            'portfolio_value': portfolio_values,
            'total_stocks': total_stocks,
            'overall_gain_loss': overall_gain_loss,
            'portfolio_datasets': portfolio_data,
            'recent_activities': recent_activites,
        }

    return render(request, 'dashboard.html', context)


@login_required(login_url='login')
def Portfolio(request):
    errors = []

    if request.method.lower() == 'post':
        company = request.POST.get('company').split('(')[0].strip()
        quantity = request.POST.get('share_quantity').strip()
        buying_rate = request.POST.get('buying_rate').strip()

        if not any([company, quantity, buying_rate]):
            errors.append('All fields are required')

        if not quantity.isdigit():
            errors.append('Quantity must be a valid number')

        if not buying_rate.isdigit():
            errors.append('Buying rate must be a valid number')

        if not errors:
            company = share_models.ListedCompanies.objects.get(name=company)
            share_models.ShareHoldings.objects.create(user_id=request.user, company_id=company, quantity=quantity, price_per_share=buying_rate)
            share_views.AddToRecentActivities(request, company, f'Added {quantity} number of shares of {company.name}')

    # Getting share names along with its abbreviation. Eg: Green Venture Limited (GVL)
    user_companies = share_models.ShareHoldings.objects.filter(user_id=request.user).values_list('company_id', flat=True)

    companies = share_models.ListedCompanies.objects.exclude(id__in=user_companies)
    serialized_companies = share_serializers.CompaniesSerializer(companies, many=True).data
    companies = [f"{company['name']} ({company['abbreviation']})" for company in serialized_companies]

    share_holdings = share_models.ShareHoldings.objects.filter(user_id=request.user).order_by('company_id__name').distinct('company_id__name')
    share_holdings = share_serializers.ShareHoldingsSerializer(share_holdings, many=True).data

    context = {
            'page_title': 'Portfolio | Stock Vault',
            'companies': json.dumps(companies),
            'share_holdings': share_holdings,
            'errors': errors,
        }

    return render(request, 'portfolio.html', context)


@login_required(login_url='login')
def Timeline(request, company_name):
    share_holdings = share_models.ShareHoldings.objects.filter(user_id=request.user, company_id__name__iexact=company_name)
    share_holdings = share_serializers.ShareHoldingsSerializer(share_holdings, many=True).data

    histories = share_models.RecentActivities.objects.filter(user_id=request.user, company_id__name=company_name)
    histories = share_serializers.RecentActivitiesSerializer(histories, many=True).data

    context = {
        'page_title': 'Portfolio | Stock Vault',
        'share_holdings': share_holdings,
        'histories': histories,
        'page_title': f'{company_name} | Stock Vault',
    }

    return render(request, 'timeline.html', context)


@login_required(login_url='login')
def WishListPage(request):
    errors = []

    if request.method.lower() == 'post':
        company_name = request.POST.get('company').split('(')[0].strip()
        company = share_models.ListedCompanies.objects.get(name=company_name)

        if share_models.WishLists.objects.filter(company_id=company).exists():
            errors.append(f'A wishlist with this name ({company_name}) already exists.')
            messages.error(request, f'A wishlist with this name ({company_name}) already exists.')

        else:
            share_models.WishLists.objects.create(user_id=request.user, company_id=company)
            share_views.AddToRecentActivities(request, company, f'{company_name} added to wishlist')

    user_companies = share_models.WishLists.objects.filter(user_id=request.user).values_list('company_id', flat=True)
    companies = share_models.ListedCompanies.objects.exclude(id__in=user_companies)

    serialized_companies = share_serializers.CompaniesSerializer(companies, many=True).data
    companies = [f"{company['name']} ({company['abbreviation']})" for company in serialized_companies]

    saved_companies = share_models.WishLists.objects.filter(user_id=request.user)
    saved_companies = share_serializers.WishlistsSerializer(saved_companies, many=True).data

    context = {
        'page_title': 'Wishlist | Stock Vault',
        'saved_companies': saved_companies,
        'companies': json.dumps(companies),
        'errors': errors,
    }

    return render(request, 'wishlist.html', context)


@login_required(login_url='login')
def ProfitLossPage(request):
    share_holdings_objs = share_models.ShareHoldings.objects.filter(user_id=request.user)
    share_holdings = share_serializers.ShareHoldingsSerializer(share_holdings_objs, many=True).data

    summary = collections.defaultdict(lambda: {
        'total_quantity': 0,
        'purchased_price': 0,
        'current_price': 0,
        'changes': 0
    })

    total_investment = 0
    total_current_value = 0

    for share_holding in share_holdings:
        company = share_holding['company_name']
        summary[company]['total_quantity'] += share_holding['quantity']

        purchase_price = share_holding['quantity'] * share_holding['price_per_share']
        current_price = share_holding['quantity'] * share_models.HistoricalPrices.objects.filter(company_id__name__iexact=company).order_by('-recorded_at').first().opening_price

        summary[company]['purchased_price'] += purchase_price
        summary[company]['current_price'] += current_price
        summary[company]['changes'] = current_price - purchase_price

        total_investment += purchase_price
        total_current_value += current_price

    data = []

    for key, value in dict(summary).items():
        value.update({'company_name': key})
        data.append(value)

    context = {
        'page_title': 'Profit-Loss | StockVault',
        'companies': share_holdings,
        'profit_loss_data': data,
        'total_investment': total_investment,
        'total_current_value': total_current_value,
        'total_changes': total_current_value - total_investment
    }

    return render(request, 'profit_loss.html', context)


@login_required(login_url='login')
def SettingsPage(request, errors=None):
    errors = []

    if request.method.lower() == 'post':
        if 'change_profile' in request.POST:
            errors = ChangeProfile(request)

        elif 'change_password' in request.POST:
            errors = ChangePassword(request)

        return JsonResponse({'success': True, 'errors': errors})

    context = {
        'page_title': 'Settings | Stock Vault',
        'errors': errors
    }

    return render(request, 'settings.html', context)


def ChangeProfile(request):
    errors = []

    if request.method.lower() == 'post':
        profile_image = request.FILES.get('profile_image')

        if not profile_image:
            errors.append('No file uploaded.')

        # Validate file type
        if not profile_image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            errors.append('Only JPG/PNG images are allowed.')

        # Validate file size (e.g., 5MB limit)
        if profile_image.size > 5 * 1024 * 1024:
            errors.append('File size must be less than 5MB.')

        if not errors: # Update the user's profile image
            user = user_models.CustomUser.objects.get(id=request.user.id)
            user.profile_image = profile_image
            user.save()

    return errors


def ChangePassword(request):
    errors = []

    if request.method.lower() == 'post':
        current_password = request.POST.get('current_password').strip()
        new_password = request.POST.get('new_password').strip()
        confirm_password = request.POST.get('confirm_password').strip()

        if not authenticate(request, email=request.user.email, password=current_password):
            errors.append('Either email or current password not matched')

        if not current_password or not new_password or not confirm_password:
            errors.append('All fields are required')

        if new_password != confirm_password:
            errors.append('New password and confirm password do not match')

        if not errors:
            user = request.user
            user.set_password(new_password)
            user.save()

            user = authenticate(request, email=request.user.email, password=new_password)

    return errors
