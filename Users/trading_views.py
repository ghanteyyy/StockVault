"""Personal share dealing and transaction history."""

import csv
from decimal import Decimal
from urllib.parse import urlencode
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.db.models.functions import Lower
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from Shares.models import ListedCompanies, Portfolios, Transactions
from Shares.trading import DEFAULT_CGT, holding_summary, record_transaction
from utils.calculator import charges


TRANSACTION_LABELS = {'buy': 'Purchase', 'sell': 'Sale', 'bonus': 'Bonus shares'}
PURCHASE_CHOICES = (
    ('secondary', 'Secondary market'), ('ipo', 'IPO'),
    ('fpo', 'FPO'), ('right', 'Right shares'),
)


def _form_values(request):
    source = request.POST if request.method == 'POST' else request.GET
    transaction_type = (source.get('transaction_type') or 'buy').strip().lower()
    company = source.get('company')
    if request.method == 'POST' and transaction_type == 'bonus':
        company = source.get('bonus_company', company)
    return {
        'company': (company or '').strip(),
        'transaction_type': transaction_type,
        'quantity': (source.get('quantity') or '').strip(),
        'unit_price': (source.get('unit_price') or '').strip(),
        'purchase_type': (source.get('purchase_type') or 'secondary').strip(),
        'cgt_type': (source.get('cgt_type') or DEFAULT_CGT).strip(),
        'transaction_date': (source.get('transaction_date') or timezone.localdate().isoformat()).strip(),
        'notes': (source.get('notes') or '').strip(),
        'idempotency_key': (request.POST.get('idempotency_key') or '').strip() or uuid4().hex,
    }


def _positions(user):
    positions = []
    for portfolio in Portfolios.objects.filter(
        user_id=user, number_of_shares__gt=0,
    ).select_related('company_id').order_by('company_id__name'):
        try:
            summary = holding_summary(portfolio)
        except ValidationError:
            summary = {'quantity': portfolio.number_of_shares, 'total_cost': portfolio.total_cost,
                       'average_cost': None, 'break_even_price': None}
        positions.append({'portfolio': portfolio, 'company': portfolio.company_id, **summary})
    return positions


@never_cache
@login_required(login_url='login')
@require_http_methods(['GET', 'HEAD', 'POST'])
def TradePage(request):
    values = _form_values(request)
    if request.method == 'GET' and request.GET.get('quote') == '1':
        portfolio = Portfolios.objects.filter(
            user_id=request.user, company_id_id=values['company'], number_of_shares__gt=0,
        ).first()
        if portfolio is None:
            return JsonResponse({'holding': None})
        try:
            selling = values['transaction_type'] == 'sell'
            summary = holding_summary(
                portfolio,
                quantity=values['quantity'] if selling else None,
                cgt_type=values['cgt_type'] if selling else DEFAULT_CGT,
            )
        except ValidationError as error:
            return JsonResponse({'errors': error.messages}, status=400)
        return JsonResponse({'holding': summary})

    errors = []
    if request.method == 'POST':
        company = ListedCompanies.objects.filter(pk=values['company']).first()
        if company is None:
            errors.append('Choose a company from the list.')
        if not errors:
            try:
                entry = record_transaction(
                    user=request.user, company=company,
                    transaction_type=values['transaction_type'], quantity=values['quantity'],
                    unit_price='0' if values['transaction_type'] == 'bonus' else values['unit_price'],
                    purchase_type=values['purchase_type'] if values['transaction_type'] == 'buy' else 'secondary',
                    cgt_type=values['cgt_type'] if values['transaction_type'] == 'sell' else DEFAULT_CGT,
                    transaction_date=values['transaction_date'], notes=values['notes'],
                    idempotency_key=values['idempotency_key'],
                )
            except ValidationError as error:
                errors.extend(error.messages)
            else:
                label = TRANSACTION_LABELS.get(entry.transaction_type, 'Transaction')
                messages.success(request, f'{label} recorded for {company.name}. Your holdings and history are up to date.')
                selection = urlencode({'company': company.pk, 'transaction_type': entry.transaction_type})
                return redirect(f"{reverse('trades')}?{selection}")

    positions = _positions(request.user)
    holding_data = {
        str(position['company'].pk): {
            key: position[key] for key in ('quantity', 'total_cost', 'average_cost', 'break_even_price')
        } for position in positions
    }
    selected_position = next((position for position in positions
                              if str(position['company'].pk) == values['company']), None)
    return render(request, 'users/trades.html', {
        'page_title': 'Buy & sell | StockVault', 'form_values': values, 'errors': errors,
        'companies': ListedCompanies.objects.order_by('name'), 'positions': positions,
        'holding_data': holding_data, 'selected_position': selected_position,
        'position_count': len(positions), 'share_count': sum(item['quantity'] for item in positions),
        'invested_total': sum((item['total_cost'] or Decimal('0') for item in positions), Decimal('0')),
        'purchase_choices': PURCHASE_CHOICES, 'tax_choices': tuple(charges['capital_gains_tax']),
        'today': timezone.localdate().isoformat(),
    }, status=400 if errors else 200)


def _history_filters(request, queryset):
    filters = {key: (request.GET.get(key) or '').strip()[:255]
               for key in ('q', 'type', 'date_from', 'date_to')}
    errors = []
    if filters['q']:
        queryset = queryset.filter(Q(company_id__name__icontains=filters['q'])
                                   | Q(company_id__abbreviation__icontains=filters['q']))
    if filters['type']:
        if filters['type'] in TRANSACTION_LABELS:
            queryset = queryset.filter(normalized_type=filters['type'])
        else:
            errors.append('Choose a valid transaction type.')
    bounds = {}
    for name in ('date_from', 'date_to'):
        if not filters[name]:
            continue
        try:
            value = parse_date(filters[name])
        except (ValueError, TypeError):
            value = None
        if value is None:
            errors.append('Enter valid dates for your history filters.')
        else:
            bounds[name] = value
    if bounds.get('date_from') and bounds.get('date_to') and bounds['date_from'] > bounds['date_to']:
        errors.append('The start date must be on or before the end date.')
    if errors:
        return queryset.none(), filters, errors
    if bounds.get('date_from'):
        queryset = queryset.filter(transaction_date__gte=bounds['date_from'])
    if bounds.get('date_to'):
        queryset = queryset.filter(transaction_date__lte=bounds['date_to'])
    return queryset, filters, errors


def _csv_cell(value):
    if value is None:
        return ''
    if isinstance(value, (int, float, Decimal)):
        return value
    value = str(value)
    formula_prefixes = ('=', '+', '-', '@', '＝', '＋', '－', '＠')
    if value.lstrip().startswith(formula_prefixes) or value.startswith(('\t', '\r', '\n')):
        return "'" + value
    return value


def _export_history(queryset):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="stockvault-transactions.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(('Date', 'Company', 'Symbol', 'Type', 'Shares', 'Unit price (NPR)',
                     'Gross amount (NPR)', 'Fees (NPR)', 'Tax (NPR)', 'Net amount (NPR)',
                     'Realized gain/loss (NPR)', 'Historical recorded total (NPR)', 'Notes', 'Record'))
    for entry in queryset.iterator():
        detailed = not entry.is_legacy
        writer.writerow([_csv_cell(value) for value in (
            entry.transaction_date, entry.company_id.name, entry.company_id.abbreviation,
            TRANSACTION_LABELS.get(entry.normalized_type, entry.transaction_type), entry.number_of_shares,
            entry.unit_price if detailed else None,
            entry.gross_amount if detailed else None,
            entry.fees if detailed else None,
            entry.capital_gains_tax if detailed else None,
            entry.net_amount if detailed else None,
            entry.realized_gain if entry.normalized_type == 'sell' and detailed else None,
            entry.transacted_price if entry.is_legacy else None,
            entry.notes, 'Historical record' if entry.is_legacy else 'Recorded transaction',
        )])
    return response


@never_cache
@login_required(login_url='login')
@require_http_methods(['GET', 'HEAD'])
def TransactionHistory(request):
    queryset = Transactions.objects.filter(user_id=request.user).select_related('company_id').annotate(
        normalized_type=Lower('transaction_type'),
    )
    queryset, filters, errors = _history_filters(request, queryset)
    queryset = queryset.order_by('-transaction_date', '-created_at', '-pk')
    if request.GET.get('export') == 'csv' and not errors:
        return _export_history(queryset)
    totals = queryset.aggregate(
        purchases=Sum('net_amount', filter=Q(normalized_type='buy', is_legacy=False)),
        sales=Sum('net_amount', filter=Q(normalized_type='sell', is_legacy=False)),
        bonus_shares=Sum('number_of_shares', filter=Q(normalized_type='bonus', is_legacy=False)),
        count=Count('pk'), legacy_count=Count('pk', filter=Q(is_legacy=True)),
    )
    page = Paginator(queryset, 20).get_page(request.GET.get('page'))
    return render(request, 'users/transactions.html', {
        'page_title': 'Transactions | StockVault', 'entries': page,
        'page_obj': page, 'filters': filters, 'errors': errors, 'totals': totals,
        'query_string': urlencode({key: value for key, value in filters.items() if value}),
    })
