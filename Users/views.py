import json
import collections
import datetime as dt
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
import Shares.views as share_views
import Users.models as user_models
import Shares.models as share_models
import Shares.serializers as share_serializers


def HomePage(request):
    return render(request, 'index.html', {'page_title': 'Stock Vault – Smarter Stock Tracking'})


def LoginPage(request):
    next_url = request.POST.get('next', request.GET.get('next', 'dashboard'))

    if request.method.lower() == 'post':
        email = request.POST.get('email')

        if user_models.CustomUser.objects.filter(email=email).exists() is False:
            messages.error(request, 'Credentials not matched')

            return redirect('login')

        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user:
            login(request, user)

            return redirect(next_url)

    return render(request, 'login.html', {'page_title': 'Stock Vault | Login', 'next': next_url})


def SignupPage(request):
    if request.method.lower() == 'post':
        email = request.POST.get('email')

        if user_models.CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')

            return redirect('signup')

        gender = request.POST.get('gender')
        name = request.POST.get('fullName')
        password = request.POST.get('password')
        profile = request.FILES['profilePicture']
        dob = dt.datetime.strptime(request.POST.get('dob'), '%Y/%m/%d')

        new_user = user_models.CustomUser(
            email=email,
            name=name,
            gender=gender,
            date_of_birth=dob
        )

        new_user.profile_image = profile
        new_user.set_password(password)
        new_user.save()

        return LoginPage(request)

    return render(request, 'signup.html', {'page_title': 'Stock Vault | Register'})


def Logout(request):
    logout(request)

    return redirect('index')


@login_required(login_url='login')
def Dashboard(request):
    total_stocks = 0
    portfolio_data = []
    portfolio_values = 0
    previous_portfolio_values = 0
    share_holdings = share_models.ShareHoldings.objects.filter(user_id=request.user)

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

    recent_activites = share_models.RecentActivities.objects.filter(user_id=request.user)
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
    if request.method == 'POST':
        company = request.POST.get('company').split('(')[0].strip()
        quantity = request.POST.get('share_quantity')
        buying_rate = request.POST.get('buying_rate')

        company = share_models.ListedCompanies.objects.get(name=company)
        share_models.ShareHoldings.objects.create(user_id=request.user, company_id=company, quantity=quantity, price_per_share=buying_rate)
        share_views.AddToRecentActivities(request, company, f'Added {quantity} number of shares of {company.name}')

        return redirect('portfolio')

    # Getting share names along with its abbreviation. Eg: Green Venture Limited (GVL)
    user_companies = share_models.ShareHoldings.objects.filter(user_id=request.user).values_list('company_id', flat=True)

    companies = share_models.ListedCompanies.objects.exclude(id__in=user_companies)
    serialized_companies = share_serializers.CompaniesSerializer(companies, many=True).data
    companies = [f"{company['name']} ({company['abbreviation']})" for company in serialized_companies]

    share_holdings = share_models.ShareHoldings.objects.filter(user_id=request.user)
    share_holdings = share_serializers.ShareHoldingsSerializer(share_holdings, many=True).data

    context = {
            'page_title': 'Portfolio | Stock Vault',
            'companies': json.dumps(companies),
            'share_holdings': share_holdings,
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
    if request.method == 'POST':
        company_name = request.POST.get('company').split('(')[0].strip()
        company = share_models.ListedCompanies.objects.get(name=company_name)

        if share_models.WishLists.objects.filter(company_id=company).exists():
            messages.error(request, f'A wishlist with this name ({company_name}) already exists.')

        else:
            share_models.WishLists.objects.create(user_id=request.user, company_id=company)
            share_views.AddToRecentActivities(request, company, f'{company_name} added to wishlist')

        return redirect('wishlist')

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
