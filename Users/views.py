import datetime as dt
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from Users.models import *
from Shares.models import *
from . import fetch_models


def HomePage(request):
    return render(request, 'index.html', {'page_title': 'Stock Vault – Smarter Stock Tracking'})


def LoginPage(request):
    if request.method.lower() == 'post':
        email = request.POST.get('email')

        if CustomUser.objects.filter(email=email).exists() is False:
            messages.error(request, 'Credentials not matched')

            return render(request, 'login.html', {'page_title': 'Stock Vault | Login'})

        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user:
            login(request, user)

            return redirect('dashboard')

    return render(request, 'login.html', {'page_title': 'Stock Vault | Login'})


def SignupPage(request):
    if request.method.lower() == 'post':
        email = request.POST.get('email')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')

            return render(request, 'signup.html', {'page_title': 'Stock Vault | Register'})

        gender = request.POST.get('gender')
        name = request.POST.get('fullName')
        password = request.POST.get('password')
        profile = request.FILES['profilePicture']
        dob = dt.datetime.strptime(request.POST.get('dob'), '%Y/%m/%d')

        new_user = CustomUser(
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


def Dashboard(request):
    total_stocks = 0
    portfolio_data = []
    portfolio_values = 0
    previous_portfolio_values = 0
    share_holdings = ShareHoldings.objects.filter(user_id=request.user)

    for index, share_holding in enumerate(share_holdings):
        total_stocks += share_holding.quantity

        historical_prices = HistoricalPrices.objects.filter(company_id=share_holding.company_id)

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

    overall_gain_loss = round(((portfolio_values - previous_portfolio_values) / portfolio_values) * 100, 2)
    recent_activites = fetch_models.fetch_recent_activities(request)

    context = {
            'page_title': 'Dashboard | Stock Vault',
            'portfolio_value': portfolio_values,
            'total_stocks': total_stocks,
            'overall_gain_loss': overall_gain_loss,
            'portfolio_datasets': portfolio_data,
            'recent_activities': recent_activites
        }

    return render(request, 'dashboard.html', context)
