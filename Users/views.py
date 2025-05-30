import datetime
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from Users.models import *


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
        dob = datetime.datetime.strptime(request.POST.get('dob'), '%Y/%m/%d')

        new_user = CustomUser(
            email=email,
            name=name,
            gender=gender,
            date_of_birth=dob
        )

        new_user.profile_image = profile
        new_user.set_password(password)
        new_user.save()

    return render(request, 'signup.html', {'page_title': 'Stock Vault | Register'})
