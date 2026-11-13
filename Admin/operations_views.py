'''Reporting and operational oversight for the custom admin area
'''

from datetime import timedelta
import math

from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, F, OuterRef, Q, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date

from Shares.models import ListedCompanies, Portfolios, Transactions
from Users.models import Targets
from .access import staff_required
from .utils import csv_response, paginate_queryset, pagination_context
from .trading_views import management_options


def _text(request, name, limit=255):
    return (request.GET.get(name) or '').strip()[:limit]


def _finite(value):
    '''Avoid presenting a corrupt legacy float as a financial summary.'''
    return value if value is not None and math.isfinite(float(value)) else 0


def _invalid_target_range():
    return (Q(low_target__isnull=True) | Q(high_target__isnull=True)
            | Q(low_target__lte=0) | Q(high_target__lte=0)
            | Q(low_target__gte=F('high_target')))


def _common_filters(request, queryset, prefix=''):
    filters = {name: _text(request, name) for name in (
        'q', 'user', 'company', 'type', 'state', 'status', 'sector',
        'date_from', 'date_to', 'sort',
    )}

    if filters['q']:
        query = Q()

        for name in ('user_id__email', 'user_id__name', 'company_id__name', 'company_id__abbreviation'):
            query |= Q(**{f'{prefix}{name}__icontains': filters['q']})
        queryset = queryset.filter(query)

    if filters['user']:
        queryset = queryset.filter(**{f'{prefix}user_id__email__iexact': filters['user']})

    if filters['company']:
        queryset = queryset.filter(**{f'{prefix}company_id_id': filters['company']})

    return queryset, filters


def _date_filters(queryset, filters, field, datetime_field=False):
    errors, bounds = {}, {}

    for name in ('date_from', 'date_to'):
        value = filters[name]

        if not value:
            continue

        try:
            parsed = parse_date(value)

        except (TypeError, ValueError):
            parsed = None

        if parsed is None:
            errors[name] = 'Enter a valid date.'

        else:
            bounds[name] = parsed

    if bounds.get('date_from') and bounds.get('date_to') and bounds['date_from'] > bounds['date_to']:
        errors['date_to'] = 'The end date must be on or after the start date.'

        return queryset, errors

    lookup = f'{field}__date' if datetime_field else field

    if 'date_from' in bounds:
        queryset = queryset.filter(**{f'{lookup}__gte': bounds['date_from']})

    if 'date_to' in bounds:
        queryset = queryset.filter(**{f'{lookup}__lte': bounds['date_to']})

    return queryset, errors


def _ordered(queryset, filters, options, default):
    selected = filters['sort'] if filters['sort'] in options else default
    filters['sort'] = selected

    return queryset.order_by(*options[selected][1]), [(key, value[0]) for key, value in options.items()]


def _record_context(request, queryset, kind, title, description, filters, metrics, sorts, errors=None):
    page = paginate_queryset(request, queryset)

    context = {
        **pagination_context(request, page),
        'record_kind': kind, 'page_title': title, 'nav_section': kind,
        'record_description': description, 'filters': filters,
        'metrics': metrics, 'sort_options': sorts, 'filter_errors': errors or {},
        'sectors': list(ListedCompanies.objects.exclude(sector='').values_list('sector', flat=True).distinct().order_by('sector')),
        'company_options': ListedCompanies.objects.order_by('abbreviation', 'pk').values('id', 'name', 'abbreviation'),
    }

    # Compatibility aliases keep links from existing user-detail pages useful.
    context[kind] = page

    return context


@staff_required
def AdminPortfolios(request):
    queryset, filters = _common_filters(request, Portfolios.objects.select_related('user_id', 'company_id'))
    status = filters['status'] if filters['status'] in ('positive', 'empty', 'invalid') else ''
    filters['status'] = status

    if status == 'positive':
        queryset = queryset.filter(number_of_shares__gt=0)

    elif status == 'empty':
        queryset = queryset.filter(Q(number_of_shares__lte=0) | Q(number_of_shares__isnull=True))

    elif status == 'invalid':
        queryset = queryset.filter(Q(number_of_shares__lt=0) | Q(total_cost__lt=0))

    queryset, errors = _date_filters(queryset, filters, 'created_at', True)
    queryset, sorts = _ordered(queryset, filters, {
        'newest': ('Newest first', ('-created_at', '-pk')),
        'oldest': ('Oldest first', ('created_at', 'pk')),
        'shares_desc': ('Most shares', ('-number_of_shares', 'pk')),
        'cost_desc': ('Highest recorded cost', ('-total_cost', 'pk')),
        'company': ('Company A–Z', ('company_id__name', 'pk')),
        'user': ('Account A–Z', ('user_id__email', 'pk')),
    }, 'newest')

    if request.GET.get('export') == 'csv':
        return csv_response('stockvault-holdings.csv',
            ['Holding ID', 'Account email', 'Account name', 'Symbol', 'Company', 'Sector', 'Shares', 'Recorded cost (NPR)', 'Created'],
            ((row.pk, row.user_id.email, row.user_id.name, row.company_id.abbreviation, row.company_id.name,
              row.company_id.sector, row.number_of_shares, row.total_cost, row.created_at.isoformat())
             for row in queryset.iterator(chunk_size=1000)))

    summary = queryset.aggregate(count=Count('pk'), shares=Sum('number_of_shares'), cost=Sum('total_cost'), accounts=Count('user_id', distinct=True))
    metrics = [
        {'label': 'Matching holdings', 'value': summary['count'], 'hint': 'Across the current filters'},
        {'label': 'Shares recorded', 'value': summary['shares'] or 0, 'hint': 'Combined recorded quantities'},
        {'label': 'Recorded cost', 'value': _finite(summary['cost']), 'kind': 'money', 'hint': 'Acquisition cost of shares still held'},
        {'label': 'Accounts represented', 'value': summary['accounts'], 'hint': 'Distinct account holders'},
    ]

    ledger_entries = Transactions.objects.filter(
        user_id_id=OuterRef('user_id_id'), company_id_id=OuterRef('company_id_id'), is_legacy=False,
    )
    context = _record_context(request, queryset.annotate(has_ledger_entries=Exists(ledger_entries)), 'portfolios', 'Holdings',
        'Manage opening balances and review holdings kept in sync with each member’s transactions.', filters, metrics, sorts, errors)
    context.update(management_options('portfolios'))

    return render(request, 'admin/portfolios.html', context)


@staff_required
def AdminTransactions(request):
    queryset, filters = _common_filters(request, Transactions.objects.select_related('user_id', 'company_id'))
    filters['type'] = filters['type'] if filters['type'] in ('buy', 'sell', 'bonus') else ''

    if filters['type']:
        queryset = queryset.filter(transaction_type__iexact=filters['type'])

    queryset, errors = _date_filters(queryset, filters, 'transaction_date')
    queryset, sorts = _ordered(queryset, filters, {
        'newest': ('Newest transactions', ('-transaction_date', '-created_at', '-pk')),
        'oldest': ('Oldest transactions', ('transaction_date', 'created_at', 'pk')),
        'value_desc': ('Highest recorded value', ('-transacted_price', 'pk')),
        'shares_desc': ('Most shares', ('-number_of_shares', 'pk')),
        'company': ('Company A–Z', ('company_id__name', 'pk')),
    }, 'newest')

    if request.GET.get('export') == 'csv':
        return csv_response('stockvault-transactions.csv',
            ['Transaction ID', 'Account email', 'Symbol', 'Company', 'Type', 'Shares', 'Recorded value (NPR)', 'Transaction date',
             'Unit price (NPR)', 'Gross amount (NPR)', 'Fees (NPR)', 'Capital gains tax (NPR)', 'Realized gain (NPR)', 'Record source', 'Notes'],
            ((row.pk, row.user_id.email, row.company_id.abbreviation, row.company_id.name, row.transaction_type,
              row.number_of_shares, row.transacted_price if row.is_legacy else row.net_amount, row.transaction_date.isoformat(), row.unit_price,
              None if row.is_legacy else row.gross_amount, None if row.is_legacy else row.fees,
              None if row.is_legacy else row.capital_gains_tax,
              row.realized_gain if not row.is_legacy and row.transaction_type == 'sell' else None,
              'Historical record' if row.is_legacy else 'Holding ledger', row.notes)
             for row in queryset.iterator(chunk_size=1000)))

    summary = queryset.aggregate(count=Count('pk'), buys=Count('pk', filter=Q(transaction_type__iexact='buy')),
        sells=Count('pk', filter=Q(transaction_type__iexact='sell')), bonuses=Count('pk', filter=Q(transaction_type__iexact='bonus')))

    metrics = [
        {'label': 'Matching transactions', 'value': summary['count'], 'hint': 'Across the current filters'},
        {'label': 'Buy records', 'value': summary['buys'], 'hint': 'Recorded purchases'},
        {'label': 'Sell records', 'value': summary['sells'], 'hint': 'Recorded sales'},
        {'label': 'Bonus records', 'value': summary['bonuses'], 'hint': 'Share allocations without purchase cost'},
    ]

    context = _record_context(request, queryset, 'transactions', 'Transactions',
        'Record purchases, sales, and bonus shares. Corrections automatically recalculate the affected holding.', filters, metrics, sorts, errors)
    context.update(management_options('transactions'))

    return render(request, 'admin/transactions.html', context)


@staff_required
def AdminTargets(request):
    url = reverse('admin-wishlists')
    query = request.GET.urlencode()
    return redirect(f'{url}?{query}' if query else url)


@staff_required
def AdminWishlists(request):
    queryset, filters = _common_filters(request, Targets.objects.select_related('user_id', 'company_id'))
    if filters['sector']:
        queryset = queryset.filter(company_id__sector=filters['sector'])

    filters['type'] = filters['type'] if filters['type'] in ('buy', 'sell') else ''

    if filters['type']:
        queryset = queryset.filter(target_type=filters['type'])

    filters['state'] = filters['state'] if filters['state'] in ('active', 'removed', 'invalid', 'all') else 'active'

    if filters['state'] == 'active':
        queryset = queryset.filter(is_deleted=False)

    elif filters['state'] == 'removed':
        queryset = queryset.filter(is_deleted=True)

    elif filters['state'] == 'invalid':
        queryset = queryset.filter(_invalid_target_range(), is_deleted=False)

    queryset, errors = _date_filters(queryset, filters, 'created_at', True)
    queryset, sorts = _ordered(queryset, filters, {
        'newest': ('Newest targets', ('-created_at', '-pk')),
        'oldest': ('Oldest targets', ('created_at', 'pk')),
        'company': ('Company A–Z', ('company_id__name', 'pk')),
        'low_target': ('Lowest target first', ('low_target', 'pk')),
        'high_target': ('Highest target first', ('-high_target', 'pk')),
        'user': ('Account A–Z', ('user_id__email', 'pk')),
        'sector': ('Sector A–Z', ('company_id__sector', 'pk')),
    }, 'newest')

    if request.GET.get('export') == 'csv':
        return csv_response('stockvault-wishlist.csv',
            ['Target ID', 'Account email', 'Symbol', 'Company', 'Type', 'Low target (NPR)', 'High target (NPR)', 'State', 'Created'],
            ((row.pk, row.user_id.email, row.company_id.abbreviation, row.company_id.name, row.target_type,
              row.low_target, row.high_target, 'Removed' if row.is_deleted else 'Active', row.created_at.isoformat())
             for row in queryset.iterator(chunk_size=1000)))

    summary = queryset.aggregate(count=Count('pk'), buys=Count('pk', filter=Q(target_type='buy')),
        sells=Count('pk', filter=Q(target_type='sell')), accounts=Count('user_id', distinct=True))

    metrics = [
        {'label': 'Matching targets', 'value': summary['count'], 'hint': 'Across the current filters'},
        {'label': 'Buy targets', 'value': summary['buys'], 'hint': 'User-defined buy ranges'},
        {'label': 'Sell targets', 'value': summary['sells'], 'hint': 'User-defined sell ranges'},
        {'label': 'Accounts represented', 'value': summary['accounts'], 'hint': 'Distinct account holders'},
    ]

    return render(request, 'admin/records.html', _record_context(request, queryset, 'wishlists', 'Wishlist',
        'Review members’ buy and sell price targets, including removed or incomplete records.', filters, metrics, sorts, errors))


@staff_required
def AdminActivity(request):
    filters = {name: _text(request, name) for name in ('q', 'action', 'date_from', 'date_to')}
    queryset = LogEntry.objects.select_related('user', 'content_type')

    if filters['q']:
        value = filters['q']
        queryset = queryset.filter(Q(user__email__icontains=value) | Q(user__name__icontains=value)
            | Q(object_repr__icontains=value) | Q(change_message__icontains=value) | Q(content_type__model__icontains=value))

    action_types = {'addition': ADDITION, 'change': CHANGE, 'deletion': DELETION}
    filters['action'] = filters['action'] if filters['action'] in action_types else ''

    if filters['action']:
        queryset = queryset.filter(action_flag=action_types[filters['action']])

    queryset, errors = _date_filters(queryset, filters, 'action_time', True)
    queryset = queryset.order_by('-action_time', '-pk')

    if request.GET.get('export') == 'csv':
        return csv_response('stockvault-admin-activity.csv', ['Time', 'Administrator', 'Action', 'Record type', 'Record', 'Details'],
            ((row.action_time.isoformat(), row.user.email, row.get_action_flag_display(),
              row.content_type.model if row.content_type else '', row.object_repr, row.get_change_message())
             for row in queryset.iterator(chunk_size=1000)))

    summary = queryset.aggregate(count=Count('pk'), admins=Count('user_id', distinct=True),
        additions=Count('pk', filter=Q(action_flag=ADDITION)), changes=Count('pk', filter=Q(action_flag=CHANGE)))

    page = paginate_queryset(request, queryset)

    return render(request, 'admin/activity.html', {
        **pagination_context(request, page), 'page_title': 'Activity log', 'nav_section': 'activity',
        'filters': filters, 'filter_errors': errors,
        'metrics': [
            {'label': 'Matching actions', 'value': summary['count'], 'hint': 'Across the current filters'},
            {'label': 'Administrators', 'value': summary['admins'], 'hint': 'Distinct actors in this report'},
            {'label': 'Created records', 'value': summary['additions'], 'hint': 'Audited additions'},
            {'label': 'Updated records', 'value': summary['changes'], 'hint': 'Audited changes'},
        ],
    })


@staff_required
def AdminOverview(request):
    today = timezone.localdate()
    recent_since = today - timedelta(days=29)

    users = get_user_model().objects.all()
    user_counts = users.aggregate(total=Count('pk'), active=Count('pk', filter=Q(is_active=True)),
        admins=Count('pk', filter=Q(is_staff=True)), recent=Count('pk', filter=Q(date_joined__date__gte=recent_since, date_joined__date__lte=today)))

    holding_counts = Portfolios.objects.aggregate(total=Count('pk'), positive=Count('pk', filter=Q(number_of_shares__gt=0)),
        cost=Sum('total_cost', filter=Q(number_of_shares__gt=0)), shares=Sum('number_of_shares', filter=Q(number_of_shares__gt=0)))
    transaction_counts = Transactions.objects.aggregate(total=Count('pk'), recent=Count('pk', filter=Q(transaction_date__gte=recent_since, transaction_date__lte=today)))
    company_count = ListedCompanies.objects.count()
    active_targets = Targets.objects.filter(is_deleted=False)

    totals = {
        'users': user_counts['total'], 'active_users': user_counts['active'], 'inactive_users': user_counts['total'] - user_counts['active'],
        'admin_users': user_counts['admins'], 'new_users_30d': user_counts['recent'],
        'companies': company_count, 'sectors': ListedCompanies.objects.exclude(sector='').values('sector').distinct().count(),
        'holdings': holding_counts['total'], 'positive_holdings': holding_counts['positive'],
        'recorded_capital': _finite(holding_counts['cost']), 'shares': holding_counts['shares'] or 0,
        'transactions': transaction_counts['total'],
        'transactions_30d': transaction_counts['recent'], 'wishlist_entries': active_targets.count(),
    }

    sectors = list(Portfolios.objects.filter(number_of_shares__gt=0).values('company_id__sector').annotate(count=Count('pk')).order_by('-count', 'company_id__sector')[:6])
    sector_breakdown = [{'name': row['company_id__sector'] or 'Unclassified', 'count': row['count'],
        'percentage': round(row['count'] / holding_counts['positive'] * 100, 1) if holding_counts['positive'] else 0} for row in sectors]
    start_week = today - timedelta(days=6)
    daily_counts = dict(users.filter(date_joined__date__gte=start_week, date_joined__date__lte=today)
        .annotate(day=TruncDate('date_joined')).values('day').annotate(count=Count('pk')).values_list('day', 'count'))
    daily_signups = [{'date': start_week + timedelta(days=day), 'count': daily_counts.get(start_week + timedelta(days=day), 0)} for day in range(7)]

    quality_signals = [
        {'label': 'Companies missing a sector', 'value': ListedCompanies.objects.filter(Q(sector='') | Q(sector__isnull=True)).count(),
         'hint': 'Complete the directory to improve sector reporting.', 'url': reverse('admin-companies') + '?sector=__missing__'},
        {'label': 'Empty holdings', 'value': Portfolios.objects.filter(Q(number_of_shares__lte=0) | Q(number_of_shares__isnull=True)).count(),
         'hint': 'Review zero, negative, or missing quantities without changing the ledger.', 'url': reverse('admin-portfolios') + '?status=empty'},
        {'label': 'Targets needing review', 'value': active_targets.filter(_invalid_target_range()).count(),
         'hint': 'Active targets with missing or invalid price ranges.', 'url': reverse('admin-wishlists') + '?state=invalid'},
    ]

    return render(request, 'admin/dashboard.html', {
        'page_title': 'Overview', 'nav_section': 'overview', 'totals': totals,
        'metrics': [
            {'label': 'Accounts', 'value': user_counts['total'], 'hint': f"{user_counts['active']} active · {user_counts['recent']} joined in 30 days"},
            {'label': 'Listed companies', 'value': company_count, 'hint': f"{totals['sectors']} recorded sectors"},
            {'label': 'Recorded capital', 'value': totals['recorded_capital'], 'kind': 'money', 'hint': 'Purchase cost of positive holdings'},
            {'label': 'Transactions · 30 days', 'value': transaction_counts['recent'], 'hint': f"{transaction_counts['total']} recorded transactions overall"},
        ],
        'recent_users': users.order_by('-date_joined', '-pk')[:5],
        'recent_transactions': Transactions.objects.select_related('user_id', 'company_id')[:6],
        'recent_activity': LogEntry.objects.select_related('user', 'content_type').order_by('-action_time', '-pk')[:6],
        'sector_breakdown': sector_breakdown, 'daily_signups': daily_signups,
        'quality_signals': quality_signals,
    })
