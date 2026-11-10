import re
import json
import datetime as dt
import math
import warnings
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST, require_safe
import Users.models as user_models
import Shares.models as share_models
from django_ratelimit.decorators import ratelimit
import Shares.serializers as share_serializers
from utils import captcha as Captcha
from .portfolio_views import DashboardPage, DeleteProtfolio, Portfolio
from .target_quotes import market_prices as _target_market_prices


@ratelimit(key='ip', rate='100/m', block=True)
def HomePage(request):
    '''
    Display the public homepage or open its calculator from the workspace.
    '''

    if request.user.is_authenticated and request.GET.get('tool') != 'trade-calculator':
        return redirect('dashboard')

    context = {
        'page_title': 'StockVault | Your investments, in focus',
    }

    return render(request, 'users/index.html', context)


@ratelimit(key='ip', rate='100/m', block=True)
def LoginPage(request):
    '''
    Sign in, keeping safe form values available after a failed attempt.
    '''

    if request.user.is_authenticated:
        return redirect('portfolio')

    next_url = request.POST.get('next', request.GET.get('next', ''))

    if not next_url or not url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        next_url = reverse('dashboard')

    errors = []
    email = ''

    if request.method.lower() == 'post':
        email = (request.POST.get('email') or '').strip()
        password = request.POST.get('password') or ''

        try:
            validate_email(email)

            if not password:
                errors.append('Enter your password.')

            else:
                user = authenticate(request, email=email, password=password)

                if user:
                    login(request, user)

                    return redirect(next_url)

                errors.append('The email or password is incorrect. Please try again.')

        except ValidationError:
            errors.append('Enter a valid email address.')

    new_captcha = Captcha.GenerateCaptcha().content
    new_captcha = json.loads(new_captcha)

    context = {
        **new_captcha,
        'errors': errors,
        'form_values': {'email': email},
        'next': next_url,
        'page_title': 'Sign in | StockVault',
    }

    return render(request, 'auth/login.html', context)


@ratelimit(key='ip', rate='100/m', block=True)
def SignupPage(request):
    '''
    Create an account with validation matching the registration form.
    '''

    errors = []
    form_values = {'name': '', 'email': '', 'dob': '', 'gender': ''}

    if request.user.is_authenticated:
        return redirect('portfolio')

    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip()
        gender = (request.POST.get('gender') or '').strip()
        name = (request.POST.get('fullName') or '').strip()
        password = request.POST.get('password') or ''
        profile = request.FILES.get('profilePicture')
        dob = (request.POST.get('dob') or '').strip()
        form_values = {'name': name, 'email': email, 'dob': dob, 'gender': gender}

        # Validating email
        try:
            validate_email(email)

            if user_models.CustomUser.objects.filter(email=email).exists():
                errors.append('An account with this email already exists. Sign in instead.')

        except ValidationError:
            errors.append('Enter a valid email address.')

        # Validating genders
        valid_genders = ['male', 'female', 'others']

        if gender not in valid_genders:
            errors.append('Choose a gender from the available options.')

        # Validating name
        if not 3 <= len(name) <= 100:
            errors.append('Enter a full name between 3 and 100 characters.')

        # Validating password
        password_regex = r'^(?=.*[A-Z])(?=.*[!@#$%^&*])(?=.*[0-9]).{8,}$'

        if not re.match(password_regex, password):
            errors.append('Password must be at least 8 characters long, contain at least one uppercase letter, one number, and one special character.')

        # Validating profile picture
        if not profile:
            errors.append('Choose a profile picture.')

        else:
            if profile.size == 0:
                errors.append('Profile picture cannot be empty.')

            if profile.size > 5 * 1024 * 1024:
                errors.append('Choose a profile picture no larger than 5 MB.')

            if not profile.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                errors.append('Only JPG/PNG images are allowed.')

        # Validating date of birth
        try:
            dob_obj = dt.datetime.strptime(dob, '%Y-%m-%d').date()
            today = timezone.localdate()
            age = today.year - dob_obj.year - ((today.month, today.day) < (dob_obj.month, dob_obj.day))

            if age < 13:
                errors.append('You must be at least 13 years old to register.')

            elif age > 110:
                errors.append('Enter a date of birth within the last 110 years.')

        except (ValueError, TypeError):
            errors.append('Enter a valid date of birth.')

        if not errors:
            new_user = user_models.CustomUser(email=email, name=name, gender=gender, date_of_birth=dob_obj)

            new_user.profile_image = profile
            new_user.set_password(password)
            new_user.save()

            return LoginPage(request)

    new_captcha = Captcha.GenerateCaptcha().content
    new_captcha = json.loads(new_captcha)

    context = {
        **new_captcha,
        'errors': errors,
        'form_values': form_values,
        'page_title': 'Create an account | StockVault',
    }

    return render(request, 'auth/signup.html', context)


@ratelimit(key='ip', rate='100/m', block=True)
def Logout(request):
    '''
    Logs out the current user and redirects them to the homepage
    '''

    logout(request)

    return redirect('index')


def _wishlist_context(request, errors=None):
    saved_companies = []
    saved_company_ids = set()
    saved_items = share_models.WishLists.objects.filter(user_id=request.user).select_related('company_id').order_by('company_id__name', 'id')

    for item in saved_items:
        company = item.company_id
        saved_company_ids.add(company.id)

        saved_companies.append({
            'id': item.id,
            'company_id': company.id,
            'company_name': company.name,
            'abbreviation': company.abbreviation,
            'sector': (company.sector or '').strip(),
        })

    available = share_models.ListedCompanies.objects.exclude(id__in=saved_company_ids).order_by('name')

    wishlist_companies = [{
        'name': company.name,
        'abbreviation': company.abbreviation,
        'sector': (company.sector or '').strip(),
    } for company in available]

    notices = {
        'added': 'The company has been added to your wishlist.',
        'removed': 'The company has been removed from your wishlist.',
    }

    return {
        'page_title': 'Wishlist | Stock Vault',
        'saved_companies': saved_companies,
        'wishlist_companies': wishlist_companies,
        'saved_company_count': len(saved_companies),
        'available_company_count': len(wishlist_companies),
        'wishlist_sector_count': len({company['sector'] for company in saved_companies if company['sector']}),
        'wishlist_notice': notices.get(request.GET.get('notice'), ''),
        'errors': errors or [],
    }


def _render_wishlist(request, *, errors=None, wishlist_form='', target_errors=None, target_form=None):
    return render(request, 'users/wishlist.html', {
        **_wishlist_context(request, errors),
        **_target_context(request),
        'wishlist_page': True,
        'wishlist_form': wishlist_form,
        'target_errors': target_errors or [],
        'target_form': target_form or {},
        'focus_targets': bool(target_errors),
    })


@ratelimit(key='ip', rate='100/m', block=True)
@login_required(login_url='login')
def WishListPage(request):
    '''
    Manage only the current user's saved companies through explicit posts
    '''

    errors = []
    company_name = ''

    if request.method == 'POST':
        action = (request.POST.get('action') or 'add').strip()

        if action == 'delete':
            wishlist_id = (request.POST.get('wishlist_id') or '').strip()

            item = share_models.WishLists.objects.filter(id=wishlist_id, user_id=request.user).first() if wishlist_id else None

            if item is None:
                errors.append('This saved company could not be found. Please refresh and try again.')

            else:
                item.delete()
                return redirect(f"{reverse('wishlist')}?notice=removed")

        elif action == 'add':
            company_name = (request.POST.get('company') or '').strip()
            company = share_models.ListedCompanies.objects.filter(name__iexact=company_name).first() if company_name else None

            if company is None:
                errors.append('Choose a company from the current list.')

            elif share_models.WishLists.objects.filter(user_id=request.user, company_id=company).exists():
                errors.append(f'{company.name} is already in your wishlist.')

            else:
                share_models.WishLists.objects.create(user_id=request.user, company_id=company)

                return redirect(f"{reverse('wishlist')}?notice=added")
        else:
            errors.append('Choose a wishlist action and try again.')

    return _render_wishlist(request, errors=errors, wishlist_form=company_name)


def _target_range(low_value, high_value):
    '''
    Validate a complete, finite and positive target range before saving
    '''

    try:
        low_target, high_target = float(low_value), float(high_value)

    except (TypeError, ValueError, OverflowError):
        return None, 'Enter valid low and high target prices.'

    if not all(math.isfinite(value) and value > 0 for value in (low_target, high_target)):
        return None, 'Target prices must be positive, finite numbers.'

    if low_target >= high_target:
        return None, 'Low target must be less than high target.'

    return (low_target, high_target), None


def _target_context(request):
    targets = []
    holdings = list(user_models.Targets.objects.filter(
        user_id=request.user, is_deleted=False,
    ).select_related('company_id').order_by('-created_at', 'id'))
    market_prices = _target_market_prices({holding.company_id.abbreviation for holding in holdings})

    for holding in holdings:
        company = holding.company_id
        market_price = market_prices.get(company.abbreviation)
        price_range, _ = _target_range(holding.low_target, holding.high_target)
        in_range = market_price is not None and price_range is not None and price_range[0] <= market_price <= price_range[1]

        targets.append({
            'id': holding.id,
            'company_name': company.name,
            'company_id': company.id,
            'abbreviation': company.abbreviation,
            'low_target': holding.low_target,
            'high_target': holding.high_target,
            'target_type': holding.target_type,
            'created_date': holding.created_at.strftime('%b %d, %Y'),
            'market_price': market_price,
            'show_buy_sell': in_range,
            'market_error': 'Market price is currently unavailable.' if market_price is None else '',
        })

    notices = {
        'created': 'Your price target has been added.',
        'updated': 'Your price target has been updated.',
        'deleted': 'Your price target has been removed.',
    }

    return {
        'targets': targets,
        'target_companies': list(share_models.ListedCompanies.objects.order_by('name').values_list('name', flat=True)),
        'target_notice': notices.get(request.GET.get('target_notice'), ''),
    }


def _target_redirect(notice=None):
    query = f'?target_notice={notice}' if notice else ''
    return redirect(f"{reverse('wishlist')}{query}#price-targets")


@login_required(login_url='login')
@require_safe
def LegacyTargetRedirect(request):
    return _target_redirect()


@ratelimit(key='ip', rate='100/m', block=True)
@login_required(login_url='login')
@require_POST
def TargetCreate(request):
    form = {field: (request.POST.get(field) or '').strip() for field in (
        'company', 'target_type', 'low_target', 'high_target',
    )}
    target_type = form['target_type']
    price_range, range_error = _target_range(form['low_target'], form['high_target'])
    errors = []

    if range_error:
        errors.append(range_error)

    if target_type not in ('buy', 'sell'):
        errors.append('Choose a buy or sell target.')

    company = share_models.ListedCompanies.objects.filter(name__iexact=form['company']).first() if form['company'] else None
    if company is None:
        errors.append('Choose a company from the current list.')

    if errors:
        return _render_wishlist(request, target_errors=errors, target_form=form)

    if user_models.Targets.objects.filter(user_id=request.user, company_id=company, target_type=target_type, is_deleted=False).exists():
        return _render_wishlist(request, target_errors=[f'A {target_type} target for {company.name} already exists.'], target_form=form)

    user_models.Targets.objects.create(
        user_id=request.user, company_id=company, target_type=target_type,
        low_target=price_range[0], high_target=price_range[1],
    )
    return _target_redirect('created')


@ratelimit(key='ip', rate='100/m', block=True)
@login_required(login_url='login')
def TargetDelete(request, company):
    '''
    Remove exactly one owned target; visiting a link never deletes data
    '''

    if request.method != 'POST':
        return _target_redirect()

    target_id = (request.POST.get('target_id') or '').strip()

    target = user_models.Targets.objects.filter(
        id=target_id, user_id=request.user, company_id=company, is_deleted=False
    ).first() if target_id else None

    if target is None:
        return _render_wishlist(request, target_errors=['This target could not be found. Please refresh and try again.'])

    target.is_deleted = True
    target.save(update_fields=['is_deleted'])

    return _target_redirect('deleted')


@ratelimit(key='ip', rate='100/m', block=True)
@login_required(login_url='login')
def TargetEdit(request):
    '''
    Update the requested owned target without mixing buy and sell records
    '''

    if request.method != 'POST':
        return _target_redirect()

    target_id = (request.POST.get('target_id') or '').strip()
    company_abbr = (request.POST.get('company_abbr') or '').strip()

    target = user_models.Targets.objects.filter(
        id=target_id, user_id=request.user, is_deleted=False
    ).select_related('company_id').first() if target_id else None

    if target is None or (company_abbr and company_abbr.casefold() != target.company_id.abbreviation.casefold()):
        return _render_wishlist(request, target_errors=['This target could not be found. Please refresh and try again.'])

    price_range, range_error = _target_range(request.POST.get('edit_low_target'), request.POST.get('edit_high_target'))

    if range_error:
        return _render_wishlist(request, target_errors=[range_error])

    target.low_target, target.high_target = price_range
    target.save(update_fields=['low_target', 'high_target'])

    return _target_redirect('updated')


@ratelimit(key='ip', rate='100/m', block=True)
@login_required(login_url='login')
def TestonomialsPage(request):
    if request.method.lower() == 'post':
        messaage = request.POST.get('testonomial').strip()

        testonomial = user_models.Testonomials(user_id=request.user, message=messaage)
        testonomial.save()

    elif request.method.lower() == 'get':
        action = request.GET.get('action', '').lower()

        if action == 'delete':
            testonomial_id = request.GET.get('testonomial_id').strip()

            user_models.Testonomials.objects.get(id__iexact=testonomial_id).delete()

            return redirect('testonomials')

    testonomials = user_models.Testonomials.objects.filter(user_id=request.user)

    companies = share_models.ListedCompanies.objects.all()

    serialized_companies = share_serializers.CompaniesSerializer(companies, many=True).data
    companies = [company['name'] for company in serialized_companies]

    context = {
        'testonomials': testonomials,
        'page_title': 'Testonomials | StockVault',
        'companies': json.dumps(companies),
    }

    return render(request, 'users/testonomials.html', context)


def _settings_image_url(user):
    '''
    A missing default photo uses the page's initials avatar
    '''

    profile_image = getattr(user, 'profile_image', None)

    if not profile_image:
        return ''

    try:
        return profile_image.url if profile_image.storage.exists(profile_image.name) else ''

    except (ValueError, OSError):
        return ''


def _settings_payload(user, field_errors=None, message=''):
    field_errors = field_errors or {}
    birth_date = getattr(user, 'date_of_birth', None)

    return {
        'success': not field_errors,
        'errors': list(field_errors.values()),
        'field_errors': field_errors,
        'message': message if not field_errors else 'Please check the highlighted fields.',
        'profile': {
            'name': user.name,
            'email': user.email,
            'gender': user.gender,
            'date_of_birth': birth_date.isoformat() if birth_date else '',
            'image_url': _settings_image_url(user),
        },
    }


def _update_settings_details(request):
    name = (request.POST.get('name') or '').strip()
    gender = (request.POST.get('gender') or '').strip()
    date_value = (request.POST.get('date_of_birth') or '').strip()

    field_errors = {}
    birth_date = None

    if not name:
        field_errors['name'] = 'Enter your full name.'

    elif len(name) > 100:
        field_errors['name'] = 'Your name must be 100 characters or fewer.'

    if gender not in ('male', 'female', 'others'):
        field_errors['gender'] = 'Choose a gender from the available options.'

    if date_value:
        try:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date_value):
                raise ValueError

            birth_date = dt.date.fromisoformat(date_value)

            if birth_date > timezone.localdate():
                field_errors['date_of_birth'] = 'Date of birth cannot be in the future.'

        except ValueError:
            field_errors['date_of_birth'] = 'Enter a valid date of birth.'

    if not field_errors:
        request.user.name = name
        request.user.gender = gender
        request.user.date_of_birth = birth_date
        request.user.save(update_fields=['name', 'gender', 'date_of_birth'])

    return _settings_payload(request.user, field_errors, 'Your personal details have been saved.')


@ratelimit(key='ip', rate='100/m', block=True)
@login_required(login_url='login')
def SettingsPage(request, errors=None):
    '''
    Save only the profile, personal details, or password the user selected
    '''

    if request.method == 'POST':
        actions = [action for action in ('update_details', 'change_profile', 'change_password') if action in request.POST]

        if len(actions) != 1:
            payload = _settings_payload(request.user, {'__all__': 'Choose one settings update and try again.'})

        elif actions[0] == 'update_details':
            payload = _update_settings_details(request)

        elif actions[0] == 'change_profile':
            payload = ChangeProfile(request)

        else:
            payload = ChangePassword(request)

        return JsonResponse(payload, status=200 if payload['success'] else 400)

    return render(request, 'users/settings.html', {
        'page_title': 'Settings | Stock Vault',
        'errors': errors or [],
        'settings_profile_image_url': _settings_image_url(request.user),
        'settings_today': timezone.localdate().isoformat(),
    })


def ChangeProfile(request):
    '''
    Validate the uploaded image before replacing the saved profile photo
    '''

    profile_image = request.FILES.get('profile_image')
    image_error = ''
    maximum_size = 5 * 1024 * 1024

    if not profile_image:
        image_error = 'Choose a PNG or JPEG photo.'

    elif not profile_image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
        image_error = 'Choose a PNG or JPEG photo.'

    elif profile_image.size > maximum_size:
        image_error = 'Your photo must be 5 MB or smaller.'

    else:
        try:
            image_bytes = profile_image.read(maximum_size + 1)

            if len(image_bytes) > maximum_size:
                image_error = 'Your photo must be 5 MB or smaller.'

            else:
                with warnings.catch_warnings():
                    warnings.simplefilter('error', Image.DecompressionBombWarning)
                    with Image.open(BytesIO(image_bytes)) as uploaded:
                        if uploaded.format not in ('PNG', 'JPEG'):
                            image_error = 'Choose a PNG or JPEG photo.'

                        else:
                            uploaded.verify()

                    if not image_error:
                        with Image.open(BytesIO(image_bytes)) as uploaded:
                            uploaded.load()
        except (UnidentifiedImageError, OSError, ValueError, SyntaxError, Image.DecompressionBombError, Image.DecompressionBombWarning):
            image_error = 'This photo could not be read. Choose a valid PNG or JPEG image.'

        finally:
            profile_image.seek(0)

    if image_error:
        return _settings_payload(request.user, {'profile_image': image_error})

    request.user.profile_image = profile_image
    request.user.save(update_fields=['profile_image'])

    return _settings_payload(request.user, message='Your profile photo has been updated.')


def ChangePassword(request):
    '''
    Validate a password change and preserve the user's current session
    '''

    current_password = request.POST.get('current_password') or ''
    new_password = request.POST.get('new_password') or ''
    confirm_password = request.POST.get('confirm_password') or ''
    field_errors = {}

    if not current_password:
        field_errors['current_password'] = 'Enter your current password.'

    elif not request.user.check_password(current_password):
        field_errors['current_password'] = 'Your current password is incorrect.'

    if not new_password:
        field_errors['new_password'] = 'Enter a new password.'

    elif not (len(new_password) >= 8 and re.search(r'[A-Z]', new_password)
              and re.search(r'[0-9]', new_password) and re.search(r'[!@#$%^&*]', new_password)):
        field_errors['new_password'] = 'Use at least 8 characters, an uppercase letter, a number, and a symbol (!@#$%^&*).'

    else:
        try:
            validate_password(new_password, user=request.user)

        except ValidationError as validation_error:
            field_errors['new_password'] = ' '.join(validation_error.messages)

    if not confirm_password:
        field_errors['confirm_password'] = 'Confirm your new password.'

    elif new_password != confirm_password:
        field_errors['confirm_password'] = 'Your new passwords do not match.'

    if not field_errors:
        request.user.set_password(new_password)
        request.user.save(update_fields=['password'])

        update_session_auth_hash(request, request.user)

    return _settings_payload(request.user, field_errors, 'Your password has been updated.')


def TradeCalculator(request):
    homepage = reverse('index')
    if request.user.is_authenticated:
        homepage += '?tool=trade-calculator'
    return redirect(f'{homepage}#trade-calculator')
