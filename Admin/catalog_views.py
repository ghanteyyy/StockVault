'''
Staff-only management of the company catalogue and question library
'''

from datetime import timedelta

from django.contrib.admin.models import ADDITION, CHANGE, DELETION
from django.db import IntegrityError, transaction
from django.db.models import Case, Exists, OuterRef, Q, Value, When, BooleanField
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from Shares.models import FAQs, ListedCompanies, Portfolios, Transactions, WishLists
from Users.models import Targets
from .access import staff_required
from .utils import csv_response, paginate_queryset, pagination_context, record_admin_action


def _error(message, errors=None, status=400):
    return JsonResponse({'status': False, 'message': message, 'errors': errors or {}}, status=status)


def _company_catalogue():
    return ListedCompanies.objects.annotate(
        has_holdings=Exists(Portfolios.objects.filter(company_id=OuterRef('pk'))),
        has_transactions=Exists(Transactions.objects.filter(company_id=OuterRef('pk'))),
        has_targets=Exists(Targets.objects.filter(company_id=OuterRef('pk'))),
        has_wishlists=Exists(WishLists.objects.filter(company_id=OuterRef('pk'))),
    ).annotate(in_use=Case(
        When(Q(has_holdings=True) | Q(has_transactions=True) | Q(has_targets=True) | Q(has_wishlists=True), then=Value(True)),
        default=Value(False), output_field=BooleanField(),
    ))


@staff_required
def AdminListedCompanies(request):
    catalogue = _company_catalogue()
    companies = catalogue

    q = request.GET.get('q', '').strip()[:255]
    sector = request.GET.get('sector', '').strip()[:255]
    usage = request.GET.get('usage', '')
    sort = request.GET.get('sort', 'symbol')
    orders = {'symbol': ('abbreviation', 'name', 'pk'), 'name': ('name', 'pk'),
              'newest': ('-created_at', 'pk'), 'oldest': ('created_at', 'pk')}

    if sort not in orders:
        sort = 'symbol'

    if q:
        companies = companies.filter(Q(name__icontains=q) | Q(abbreviation__icontains=q) | Q(sector__icontains=q))

    if sector == '__missing__':
        companies = companies.filter(Q(sector='') | Q(sector__isnull=True))

    elif sector:
        companies = companies.filter(sector=sector)

    if usage in ('in_use', 'unused'):
        companies = companies.filter(in_use=usage == 'in_use')

    else:
        usage = ''

    companies = companies.order_by(*orders[sort])

    if request.GET.get('export') == 'csv':
        return csv_response('stockvault-companies.csv', ['Symbol', 'Company', 'Sector', 'Linked records', 'Added'],
                            ((company.abbreviation, company.name, company.sector, 'Yes' if company.in_use else 'No',
                              company.created_at.isoformat()) for company in companies.iterator()))
    page = paginate_queryset(request, companies)

    context = {
        **pagination_context(request, page), 'companies': page,
        'page_title': 'Companies', 'admin_section': 'companies',
        'filters': {'q': q, 'sector': sector, 'usage': usage, 'sort': sort},
        'sectors': ListedCompanies.objects.exclude(sector='').values_list('sector', flat=True).distinct().order_by('sector'),
        'total_companies': ListedCompanies.objects.count(),
        'sector_count': ListedCompanies.objects.exclude(sector='').values('sector').distinct().count(),
        'linked_companies': catalogue.filter(in_use=True).count(),
        'missing_sectors': ListedCompanies.objects.filter(sector='').count(),
    }

    return render(request, 'admin/companies.html', context)


def _company_values(request, instance=None):
    values = {
        'name': request.POST.get('company_name', '').strip(),
        'abbreviation': request.POST.get('company_abbreviation', '').strip().upper(),
        'sector': request.POST.get('company_sector', '').strip(),
    }

    fields = {'name': ('company_name', 'company name'), 'abbreviation': ('company_abbreviation', 'symbol'),
              'sector': ('company_sector', 'sector')}

    errors = {}

    for key, (field, label) in fields.items():
        if not values[key]:
            errors[field] = f'Enter a {label}.'

        elif len(values[key]) > 255:
            errors[field] = 'Use no more than 255 characters.'

    other = ListedCompanies.objects.all()

    if instance is not None:
        other = other.exclude(pk=instance.pk)

    if values['name'] and other.filter(name__iexact=values['name']).exists():
        errors['company_name'] = 'A company with this name already exists.'

    if values['abbreviation'] and other.filter(abbreviation__iexact=values['abbreviation']).exists():
        errors['company_abbreviation'] = 'A company with this symbol already exists.'

    return values, errors


@staff_required
@require_POST
def AdminListedCompaniesAdd(request):
    values, errors = _company_values(request)

    if errors:
        return _error('Please check the company details.', errors)

    try:
        with transaction.atomic():
            company = ListedCompanies.objects.create(**values)
            record_admin_action(request, company, 'Added company to the catalogue.', action=ADDITION)

    except IntegrityError:
        return _error('This company already exists. Refresh the catalogue and try again.', status=409)

    return JsonResponse({'status': True, 'message': 'Company added to the catalogue.'})


@staff_required
@require_POST
def AdminListedCompaniesEdit(request):
    try:
        with transaction.atomic():
            company = ListedCompanies.objects.select_for_update().filter(pk=request.POST.get('company_id', '')).first()

            if company is None:
                return _error('This company could not be found.', status=404)

            values, errors = _company_values(request, company)

            if errors:
                return _error('Please check the company details.', errors)

            changed = [field for field, value in values.items() if getattr(company, field) != value]

            if changed:
                for field, value in values.items():
                    setattr(company, field, value)
                company.save(update_fields=changed)

                record_admin_action(request, company, 'Updated company: ' + ', '.join(changed) + '.', action=CHANGE)

    except IntegrityError:
        return _error('This company already exists. Refresh the catalogue and try again.', status=409)

    return JsonResponse({'status': True, 'message': 'Company details saved.'})


@staff_required
@require_POST
def AdminListedCompaniesDelete(request):
    with transaction.atomic():
        company = ListedCompanies.objects.select_for_update().filter(pk=request.POST.get('company_id', '')).first()

        if company is None:
            return _error('This company could not be found.', status=404)

        linked = (Portfolios.objects.filter(company_id=company).exists()
                  or Transactions.objects.filter(company_id=company).exists()
                  or Targets.objects.filter(company_id=company).exists()
                  or WishLists.objects.filter(company_id=company).exists())

        if linked:
            return _error('This company has linked holdings, transactions, targets, or wishlists and cannot be removed.', status=409)

        record_admin_action(request, company, 'Removed an unused company from the catalogue.', action=DELETION)
        company.delete()

    return JsonResponse({'status': True, 'message': 'Unused company removed.'})


def _incomplete_questions():
    return Q(question__isnull=True) | Q(question='') | Q(answer__isnull=True) | Q(answer='')


@staff_required
def AdminFAQs(request):
    faqs = FAQs.objects.all()
    q = request.GET.get('q', '').strip()[:255]

    completeness = request.GET.get('content', '')
    sort = request.GET.get('sort', 'newest')
    orders = {'newest': ('-created_at', 'pk'), 'oldest': ('created_at', 'pk'), 'question': ('question', 'pk')}

    if sort not in orders:
        sort = 'newest'

    if q:
        faqs = faqs.filter(Q(question__icontains=q) | Q(answer__icontains=q))

    if completeness == 'complete':
        faqs = faqs.exclude(_incomplete_questions())

    elif completeness == 'incomplete':
        faqs = faqs.filter(_incomplete_questions())

    else:
        completeness = ''

    faqs = faqs.order_by(*orders[sort])

    if request.GET.get('export') == 'csv':
        return csv_response('stockvault-question-library.csv', ['Question', 'Answer', 'Added'],
                            ((faq.question or '', faq.answer or '', faq.created_at.isoformat()) for faq in faqs.iterator()))

    page = paginate_queryset(request, faqs)

    context = {
        **pagination_context(request, page), 'faqs': page,
        'faq_records': {str(faq.pk): {'question': faq.question or '', 'answer': faq.answer or ''} for faq in page.object_list},
        'page_title': 'Question library', 'admin_section': 'faqs',
        'filters': {'q': q, 'content': completeness, 'sort': sort},
        'total_faqs': FAQs.objects.count(), 'incomplete_faqs': FAQs.objects.filter(_incomplete_questions()).count(),
        'recent_faqs': FAQs.objects.filter(created_at__gte=timezone.now() - timedelta(days=30)).count(),
    }

    return render(request, 'admin/faqs.html', context)


def _faq_values(request, instance=None):
    values = {'question': request.POST.get('faq_question', '').strip(),
              'answer': request.POST.get('faq_answer', '').strip()}
    errors = {}

    for key, value in values.items():
        if not value:
            errors[f'faq_{key}'] = f'Enter the {key}.'

        elif len(value) > 255:
            errors[f'faq_{key}'] = 'Use no more than 255 characters.'

    others = FAQs.objects.all()

    if instance is not None:
        others = others.exclude(pk=instance.pk)

    if values['question'] and others.filter(question__iexact=values['question']).exists():
        errors['faq_question'] = 'This question is already in the library.'

    return values, errors


@staff_required
@require_POST
def AdminFaqAdd(request):
    values, errors = _faq_values(request)

    if errors:
        return _error('Please check the question and answer.', errors)

    with transaction.atomic():
        faq = FAQs.objects.create(**values)
        record_admin_action(request, faq, 'Added a question to the library.', action=ADDITION)

    return JsonResponse({'status': True, 'message': 'Question added to the library.'})


@staff_required
@require_POST
def AdminFaqEdit(request):
    with transaction.atomic():
        faq = FAQs.objects.select_for_update().filter(pk=request.POST.get('faq_id', '')).first()

        if faq is None:
            return _error('This question could not be found.', status=404)

        values, errors = _faq_values(request, faq)

        if errors:
            return _error('Please check the question and answer.', errors)

        changed = [field for field, value in values.items() if getattr(faq, field) != value]

        if changed:
            for field, value in values.items():
                setattr(faq, field, value)

            faq.save(update_fields=changed)

            record_admin_action(request, faq, 'Updated a question in the library.', action=CHANGE)

    return JsonResponse({'status': True, 'message': 'Question saved.'})


@staff_required
@require_POST
def AdminFaqDelete(request):
    with transaction.atomic():
        faq = FAQs.objects.select_for_update().filter(pk=request.POST.get('faq_id', '')).first()

        if faq is None:
            return _error('This question could not be found.', status=404)

        record_admin_action(request, faq, 'Removed a question from the library.', action=DELETION)
        faq.delete()

    return JsonResponse({'status': True, 'message': 'Question removed from the library.'})
