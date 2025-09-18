import re
import json
import random
import datetime as dt
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from urllib.parse import unquote
import Shares.views as share_views
import Users.models as user_models
import Shares.models as share_models
import Users.serializers as user_serializers
import Shares.serializers as share_serializers
from Shares import scraper


def HomePage(request):
    """
    Displays the homepage of Stock Vault.

    If the user is logged in, it redirects to the dashboard page.
    Otherwise, it renders the index.html template with the page title.
    """

    if request.user.is_authenticated:
        return redirect('dashboard')

    testonomials = user_models.Testonomials.objects.all()
    testonomials = user_serializers.TestonomialsSerializer(testonomials, many=True).data
    random.shuffle(testonomials)

    faqs = share_models.FAQs.objects.all()
    faqs = share_serializers.FaqSerializers(faqs, many=True).data
    random.shuffle(faqs)

    context = {
        'page_title': 'Stock Vault – Smarter Stock Tracking',
        'testonomials': testonomials[:2],
        'faqs': faqs[:5]
    }

    return render(request, 'index.html', context)


def LoginPage(request):
    """
    Handles login functionality for the website.

    The function first looks for a POST request. If the method is POST,
    it extracts the email and password from the request, validates
    the email, and then authenticates the user. If the user is
    authenticated, it logs the user in and redirects them to the page
    specified by the 'next' parameter in the request, or to the
    dashboard page if no 'next' parameter is provided.

    If the method is not POST, it renders the login template with
    the page title and the value of the 'next' parameter.
    """

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
    """
    Handles signup functionality for the website.

    The function first looks for a POST request. If the method is POST,
    it extracts the email, gender, name, password, profile picture, and
    date of birth from the request, validates the email, gender, name,
    password, profile picture, and date of birth, and then creates a
    new user if there are no errors.

    If the method is not POST, it renders the signup template with
    the page title and the list of errors.
    """

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
            dob_obj = dt.datetime.strptime(dob, '%Y-%m-%d')

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
    """
    Logs out the current user and redirects them to the homepage
    """

    logout(request)

    return redirect('index')


@login_required(login_url='login')
def Dashboard(request):
    """
    Provides a dashboard with a portfolio overview

    This view displays a user's portfolio, including the total number
    of stocks they own, the current value of their portfolio, and the
    percentage change in the value of their portfolio over the last day.
    It also displays the five most recent activities a user has performed.
    """

    total_stocks = 0
    portfolio_data = []
    portfolio_values = 0
    overall_gain_loss = 0

    NepseIndices = (share_models.NepseIndices.objects
                    .using('stockmarketdata')
                    .order_by('date')).values_list('date', 'index_value', 'percentage_change')

    nepse_change = 'negative' if NepseIndices.last()[-1].startswith('-') else 'positive'
    NepseIndices = json.dumps(list(NepseIndices), default=str)

    share_holdings = share_models.Portfolios.objects.filter(user_id=request.user).order_by('company_id__name').distinct('company_id__name')

    for share_holding in share_holdings:
        company_name = f'{share_holding.company_id.abbreviation} ({share_holding.company_id.name})'

        qs = (share_models.StockMarketData.objects
            .using("stockmarketdata")
            .filter(company_name=company_name)
            .only("trade_date", "ltp", "pct_change", "open_price")
            .order_by("-trade_date"))[:2]     # Getting first two latest data

        if len(qs) < 2:
            portfolio_data.append(
                {
                    'error': 'No market value yet.',
                    'company_name': f'{share_holding.company_id.name} ({share_holding.company_id.abbreviation})',
                }
            )

            continue

        total_stocks += share_holding.number_of_shares

        percentage_change = qs[1].pct_change
        previous_closing_price = float(qs[1].ltp)
        previous_opening_price = float(qs[0].open_price)
        portfolio_values += share_holding.number_of_shares * previous_closing_price

        portfolio_data.append(
            {
                'company_name': f'{share_holding.company_id.name} ({share_holding.company_id.abbreviation})',
                'today_opening_price': previous_opening_price,
                'today_closing_price': previous_closing_price,
                'percentage_change': f"{percentage_change}%"
            }
        )

        overall_gain_loss += float(percentage_change)

    recent_activites = share_models.Transactions.objects.filter(user_id=request.user).order_by('-transaction_date')[:5]
    recent_activites = share_serializers.TransactionsSerializer(recent_activites, many=True).data[:5]

    context = {
            'page_title': 'Dashboard | Stock Vault',
            'portfolio_value': portfolio_values,
            'nepse_indices': NepseIndices,
            'total_stocks': total_stocks,
            'portfolio_datasets': portfolio_data,
            'recent_activities': recent_activites,
            'nepse_change': nepse_change,
            'overall_gain_loss': round(overall_gain_loss, 2),
        }

    return render(request, 'dashboard.html', context)


@login_required(login_url='login')
def Portfolio(request):
    """
    Provides a portfolio page where users can see their current portfolio and add new shares

    This view displays a user's portfolio, including the shares they own,
    the number of shares, and the total value of their portfolio. It also
    displays an input form where users can add new shares to their portfolio.
    """

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
            share_views.modify_shares(request.user, company, quantity, buying_rate, 'buy')

    # Getting share names along with its abbreviation. Eg: Green Venture Limited (GVL)
    user_companies = share_models.Portfolios.objects.filter(user_id=request.user).values_list('company_id', flat=True)

    companies = share_models.ListedCompanies.objects.exclude(id__in=user_companies)
    serialized_companies = share_serializers.CompaniesSerializer(companies, many=True).data
    companies = [f"{company['name']} ({company['abbreviation']})" for company in serialized_companies]

    share_holdings = share_models.Portfolios.objects.filter(user_id=request.user).order_by('-created_at')
    share_holdings = share_serializers.PortfoliosSerializer(share_holdings, many=True).data

    context = {
            'page_title': 'Portfolio | Stock Vault',
            'companies': json.dumps(companies),
            'share_holdings': share_holdings,
            'errors': errors,
        }

    return render(request, 'portfolio.html', context)


@login_required(login_url='login')
def PortfolioGraph(request):
    """
    Render the timeline page showing a user's share holdings and recent activities for a specific company.

    The function retrieves the company name from the GET request,
    fetches the user's share holdings and recent activities associated
    with that company, and renders the 'timeline.html' template with
    the appropriate context.
    """

    company_name = request.GET.get('company_name', '').strip()
    company_name = unquote(company_name)

    column_type = request.GET.get('column_type', 'ltp').strip()
    column_type = unquote(column_type)

    share_holdings = share_models.Portfolios.objects.filter(user_id=request.user, company_id__name__iexact=company_name)
    share_holdings = share_serializers.PortfoliosSerializer(share_holdings, many=True).data

    histories = share_models.Transactions.objects.filter(user_id=request.user, company_id__name=company_name)
    histories = share_serializers.TransactionsSerializer(histories, many=True).data

    qs = (share_models.StockMarketData.objects
        .using("stockmarketdata")
        .filter(company_name=company_name)
        .order_by("trade_date")
        .values_list("trade_date", column_type))

    graph_data = [float(v) for _, v in qs]
    graph_labels = [d.strftime("%Y-%m-%d") for d, _ in qs]
    graph_options = ['ltp', 'pct_change', 'high', 'low', 'open_price', 'qty', 'turnover']

    context = {
        'page_title': 'Portfolio | Stock Vault',
        'share_holdings': share_holdings,
        'histories': histories,
        'page_title': f'{company_name} | Stock Vault',
        'graph_labels': graph_labels,
        'graph_data': graph_data,
        'graph_options': graph_options,
    }

    return render(request, 'portfolio_graph.html', context)


@login_required(login_url='login')
def WishListPage(request):
    """
    Render the wishlist page showing a user's wishlist.

    The function retrieves the wishlist items associated with the user,
    fetches the list of companies that are not in the user's wishlist, and
    renders the 'wishlist.html' template with the appropriate context.
    """

    errors = []

    if request.method.lower() == 'post':
        company_name = request.POST.get('company').split('(')[0].strip()
        company = share_models.ListedCompanies.objects.get(name=company_name)

        if share_models.WishLists.objects.filter(company_id=company).exists():
            errors.append(f'A wishlist with this name ({company_name}) already exists.')
            messages.error(request, f'A wishlist with this name ({company_name}) already exists.')

        else:
            share_models.WishLists.objects.create(user_id=request.user, company_id=company)

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
def TargetPage(request):
    """
    Handles the logic for adding a target to buy/sell a share
    at a specific price when it reaches a certain price.
    """

    errors = []

    if request.method.lower() == 'post':
        company_name = request.POST.get('company').strip()
        low_target = request.POST.get('low_target').strip()
        high_target = request.POST.get('high_target').strip()
        target_type = request.POST.get('target_type').strip()

        if not any([company_name, low_target, high_target, target_type]):
            errors.append('All fields are required')

        try:
            float(low_target)
            float(high_target)

        except ValueError:
            errors.append('Low and high targets must be valid numbers')

        if float(low_target) >= float(high_target):
            errors.append('Low target must be less than high target')

        if target_type not in ['buy', 'sell']:
            errors.append('Invalid target type selected')

        company_name = company_name.split('(')[0].strip()
        company = share_models.ListedCompanies.objects.get(name__iexact=company_name)

        if user_models.Targets.objects.filter(user_id=request.user, company_id=company, target_type=target_type, is_deleted=False).exists():
            errors.append(f'Target for {company_name} already exists')

        if not errors:
            user_models.Targets.objects.create(
                user_id=request.user,
                company_id=company,
                low_target=float(low_target),
                high_target=float(high_target),
                target_type=target_type
            )

    # Getting share names along with its abbreviation. Eg: Green Venture Limited (GVL)
    companies = share_models.ListedCompanies.objects.all()

    serialized_companies = share_serializers.CompaniesSerializer(companies, many=True).data
    companies = [f"{company['name']} ({company['abbreviation']})" for company in serialized_companies]

    targets = user_models.Targets.objects.filter(user_id=request.user, is_deleted=False)
    targets = user_serializers.TargetsSerializer(targets, many=True).data

    for target in targets:
        market_data = scraper.get_market_data(target['abbreviation'])
        market_price = float(market_data['market_price'])

        low_target, high_target = target['low_target'], target['high_target']
        show_buy_sell = True if low_target <= market_price <= high_target else False

        target['market_price'] = market_price
        target['show_buy_sell'] = show_buy_sell

    context = {
        'errors': errors,
        'targets': targets,
        'page_title': 'Target | Stock Vault',
        'companies': json.dumps(companies),
    }

    return render(request, 'target.html', context)


@login_required(login_url='login')
def TargetDelete(request, company):
    """
    Deletes a target for a specific company.
    """

    target = user_models.Targets.objects.filter(user_id=request.user, company_id=company, is_deleted=False).first()

    if target:
        target.is_deleted = True
        target.save()

    return redirect('target')


@login_required(login_url='login')
def TargetEdit(request):
    """
    Handles the logic for editing a target for a specific company
    """

    if request.method.lower() == 'post':
        company_abbr = request.POST.get('company_abbr').strip()
        low_target = request.POST.get('edit_low_target').strip()
        high_target = request.POST.get('edit_high_target').strip()

        target = user_models.Targets.objects.filter(user_id=request.user, company_id__abbreviation__iexact=company_abbr, is_deleted=False).first()

        if target:
            low_target = float(low_target)
            high_target = float(high_target)

            target.low_target = low_target
            target.high_target = high_target

            target.save()

        return redirect('target')

@login_required(login_url='login')
def SettingsPage(request, errors=None):
    """
    Handles requests for the settings page. If the request is a POST, it validates
    the data and if the data is valid, it changes the user's profile or password.
    If the request is a GET, it renders the settings page.
    """

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
    """
    Handles a request to update a user's profile image.

    It validates the uploaded file to ensure it is a valid image
    file and has a size less than or equal to 5MB. If the file is
    valid, it updates the user's profile image.
    """

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
    """
    Handles a request to change a user's password.

    The function validates the current password and ensures that
    the new password and confirm password match. If the current
    password is correct and the passwords match, it updates the
    user's password.
    """

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


@login_required(login_url='login')
def TradeCalculator(request):
    return render(request, 'calculator.html', {'page_title': 'Calculator | Stock Vault'})
