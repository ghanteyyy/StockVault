import json
import datetime
from urllib.parse import urljoin
from django.conf import settings
from django.shortcuts import render
import Users.models as user_models
import Shares.models as share_models
from django.http import JsonResponse
from django.templatetags.static import static
from django.core.paginator import Paginator
import Users.serializers as users_serializers
import Shares.serializers as shares_serializers
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.html import escape


def paginator(request, items, items_per_page=100):
    page = request.GET.get('page') or 1
    paginator = Paginator(items, items_per_page)

    return paginator.get_page(page)


@login_required(login_url='login')
def AdminPage(request):
    all_users = user_models.CustomUser.objects.all()
    user_per_page = paginator(request=request, items=all_users, items_per_page=30)

    users_json = list(
        user_per_page.object_list.values(
            'name', 'email', 'gender', 'profile_image', 'date_of_birth', 'date_joined'
        )
    )

    media_abs = request.build_absolute_uri(settings.MEDIA_URL)
    default_avatar = request.build_absolute_uri(urljoin(media_abs, 'default.png'))

    for user in users_json:
        profile_image = user.get('profile_image')
        user['profile_image'] = urljoin(media_abs, profile_image) if profile_image else default_avatar

        joined_date = user.get('date_joined')
        user['date_joined'] = joined_date.strftime("%Y-%m-%d %I:%M:%S %p") if joined_date else None

        dob = user.get('date_of_birth')
        user['date_of_birth'] = dob.strftime('%Y-%m-%d') if dob else None

    context = {
        'user_details': user_per_page,
        'user_json': json.dumps(users_json),
        'page_title': 'Users',
    }

    return render(request, 'admin/users.html', context)


@login_required(login_url='login')
def UserProfile(request):
    user_email = request.GET.get('user')
    user = user_models.CustomUser.objects.get(email__iexact=user_email)

    context = {
        'user_profile': user,
        'page_title': 'Users',
    }

    return render(request, 'admin/profile.html', context)


@login_required(login_url='login')
def ChangeProfile(request):
    """
    Handles a request to update a user's profile image.

    It validates the uploaded file to ensure it is a valid image
    file and has a size less than or equal to 5MB. If the file is
    valid, it updates the user's profile image.
    """

    errors = []

    if request.method.lower() == 'post':
        user_email = request.POST.get('user_email')
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
            user = user_models.CustomUser.objects.get(email__iexact=user_email)
            user.profile_image = profile_image
            user.save()

    return errors


def UserChangePassword(request):
    """
    Handles a request to change a user's password.

    The function validates the current password and ensures that
    the new password and confirm password match. If the current
    password is correct and the passwords match, it updates the
    user's password.
    """

    errors = []

    if request.method.lower() == 'post':
        user_email = request.POST.get('user_email')
        user = user_models.CustomUser.objects.get(email__iexact=user_email)

        password = request.POST.get('new_password').strip()

        user.set_password(password)
        user.save()

        return JsonResponse({'success': True, 'errors': errors, 'user_email': user_email})

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
    companies = share_models.ListedCompanies.objects.all().values("name", "sector", "id", "abbreviation")

    company_per_page = paginator(request=request, items=companies)

    context = {
        'companies': company_per_page,
        'page_title': 'Listed Companies',
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


@login_required(login_url='login')
def AdminPortfolios(request):
    user_email = request.GET.get('user')

    portfolios = share_models.Portfolios.objects.filter(user_id__email__iexact=user_email)
    portfolios = shares_serializers.PortfoliosSerializer(portfolios, many=True).data

    portfolio_per_page = paginator(request=request, items=portfolios)

    context = {
        'page_title': 'Portfolios',
        'portfolios': portfolio_per_page,
    }

    return render(request, 'admin/portfolios.html', context)


@login_required(login_url='login')
def AdminPortfoliosLots(request):
    portfolioLots = share_models.PortfolioLots.objects.all()

    portfolioLots = shares_serializers.PortfolioLotsSerializer(portfolioLots, many=True).data
    portfolioLots_per_page = paginator(request=request, items=portfolioLots)

    context = {
        'page_title': 'Portfolio Lots',
        'portfolioLots': portfolioLots_per_page,
    }

    return render(request, 'admin/portfolioLots.html', context)


@login_required(login_url='login')
def AdminTransactions(request):
    user_email = request.GET.get('user')

    transactions = share_models.Transactions.objects.filter(user_id__email__iexact=user_email)
    transactions = shares_serializers.TransactionsSerializer(transactions, many=True).data

    transactions_per_page = paginator(request=request, items=transactions)

    context = {
        'page_title': 'Transactions',
        'transactions': transactions_per_page,
    }

    return render(request, 'admin/transactions.html', context)


@login_required(login_url='login')
def AdminTargets(request):
    user_email = request.GET.get('user')

    targets = user_models.Targets.objects.filter(user_id__email__iexact=user_email)
    targets = users_serializers.TargetsSerializer(targets, many=True).data

    targets_per_page = paginator(request=request, items=targets)

    context = {
        'targets': targets_per_page,
        'page_title': 'Targets',
    }

    return render(request, 'admin/targets.html', context)


@login_required(login_url='login')
def AdminWishlists(request):
    user_email = request.GET.get('user')

    wishlists = share_models.WishLists.objects.filter(user_id__email__iexact=user_email)
    wishlists = shares_serializers.WishlistsSerializer(wishlists, many=True).data

    wishlists_per_page =paginator(request=request, items=wishlists)

    context = {
        'page_title': 'Targets',
        'wishlists': wishlists_per_page,
    }

    return render(request, 'admin/wishlists.html', context)


@login_required(login_url='login')
def AdminFAQs(request):
    faqs = share_models.FAQs.objects.all()
    faqs = shares_serializers.FaqSerializers(faqs, many=True).data

    faqs_per_page = paginator(request=request, items=faqs)

    context = {
        'faqs': faqs_per_page,
        'page_title': 'FAQs',
    }

    return render(request, 'admin/faqs.html', context)


@login_required(login_url='login')
def AdminFaqAdd(request):
    if request.method.lower() == 'post':
        faq_question = request.POST.get('faq_question', '').strip()
        faq_answer = request.POST.get('faq_answer', '').strip()

        if share_models.FAQs.objects.filter(question__iexact=faq_question):
            return JsonResponse({'status': False, 'message': 'Question already exists'})

        faq = share_models.FAQs(question=faq_question, answer=faq_answer)
        faq.save()

        return JsonResponse({'status': True, 'message': 'Question added successfully'})

    return JsonResponse({'status': False, 'message': 'Something went wrong'})


@login_required(login_url='login')
def AdminFaqEdit(request):
    if request.method.lower() == 'post':
        faq_id = request.POST.get('faq_id', '').strip()
        faq_answer = request.POST.get('faq_answer', '').strip()
        faq_question = request.POST.get('faq_question', '').strip()

        if not share_models.FAQs.objects.filter(id=faq_id):
            return JsonResponse({'status': False, 'message': 'Requested FAQ does not exists'})

        faq = share_models.FAQs.objects.get(id=faq_id)
        faq.question = faq_question
        faq.answer = faq_answer
        faq.save()

        return JsonResponse({'status': True, 'message': 'FAQ information updated successfully'})

    return JsonResponse({'status': False, 'message': 'Something went wrong'})


@login_required(login_url='login')
def AdminFaqDelete(request):
    faq_id = request.GET.get('faq_id', '').strip()

    if not share_models.FAQs.objects.filter(id=faq_id):
        return JsonResponse({'status': False, 'message': 'Requested FAQ does not exist'})

    company = share_models.FAQs.objects.get(id=faq_id)
    company.delete()

    return JsonResponse({'status': True, 'message': 'FAQ deleted successfully'})


@login_required(login_url='login')
def AdminMarketData(request):
    targets = user_models.Targets.objects.all()
    targets = users_serializers.TargetsSerializer(targets, many=True).data

    table_heads = ['Company', 'Sector', 'LTP', '% Change', 'Open Price', 'Low', 'High', 'Qty', 'Turnover', 'Trade Date']

    context = {
        'page_title': 'Market Data',
        'table_heads': table_heads,
    }

    return render(request, 'admin/market_data.html', context)


DT_COLUMNS = [
    "company_name", "sector", "ltp", "pct_change", "open_price",
    "low", "high", "qty", "turnover", "trade_date"
]


@login_required(login_url='login')
def stockmarketdata_dt(request):
    draw   = int(request.GET.get("draw", 1))
    start  = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 25))
    search = request.GET.get("search[value]", "")

    qs = (share_models.StockMarketData.objects
          .using("stockmarketdata")
          .order_by("trade_date", "company_name"))

    total = qs.count()

    if search:
        qs = qs.filter(
            Q(company_name__icontains=search) |
            Q(sector__icontains=search) |
            Q(ltp__icontains=search)
        )

    filtered = qs.count()
    page = qs.values(*DT_COLUMNS)[start:start+length]

    data = [{
        "sn": i+start+1,
        "company_name": escape(r["company_name"] or ""),
        "company_abbreviation": escape(r["company_name"].split('(')[0] or ""),
        "sector": escape(r["sector"] or ""),
        "ltp": r["ltp"] or "",
        "pct_change": r["pct_change"] or "",
        "open_price": r["open_price"] or "",
        "low": r["low"] or "",
        "high": r["high"] or "",
        "qty": r["qty"] or "",
        "turnover": r["turnover"] or "",
        "trade_date": r["trade_date"].strftime("%b %d, %Y") if r["trade_date"] else ""
    } for i, r in enumerate(page)]

    return JsonResponse({
        "draw": draw,
        "recordsTotal": total,
        "recordsFiltered": filtered,
        "data": data
    })
