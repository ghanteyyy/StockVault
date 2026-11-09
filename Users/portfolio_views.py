"""Portfolio reports backed by the same balances as the trading workspace."""
import json
from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Exists, OuterRef, Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from nepse import Nepse

from Shares.models import ListedCompanies, Portfolios, Transactions
from Shares.trading import delete_holding, holding_summary, record_transaction, sale_preview
from utils.calculator import money
from utils.utils import nepali_comma


nepse = Nepse()
ZERO = Decimal('0.00')


def _market_quote(company):
    """A missing market feed must never hide recorded holdings or trades."""
    try:
        data = nepse.getCompanyDetails(company.abbreviation)['securityDailyTradeDto']
        price = Decimal(str(data['lastTradedPrice']))
        if not price.is_finite() or price <= 0:
            return None
        return data
    except Exception:
        # The external NEPSE client exposes several network/response exceptions.
        return None


@ratelimit(key='ip', rate='100/m', block=True)
@login_required(login_url='login')
def DashboardPage(request):
    holdings = list(Portfolios.objects.filter(
        user_id=request.user, number_of_shares__gt=0
    ).select_related('company_id'))
    investment = sum((row.total_cost or ZERO for row in holdings), ZERO)
    market_value = ZERO
    missing_quotes = False
    sectors = {}
    for holding in holdings:
        sector = holding.company_id.sector or 'Unclassified'
        sectors[sector] = sectors.get(sector, 0) + 1
        quote = _market_quote(holding.company_id)
        if quote is None:
            missing_quotes = True
        else:
            market_value += Decimal(str(quote['lastTradedPrice'])) * holding.number_of_shares
    sales = Transactions.objects.filter(
        user_id=request.user, transaction_type='sell', is_legacy=False,
    ).aggregate(total=Sum('net_amount'))['total'] or ZERO
    value_change = market_value - investment
    percentage = None if missing_quotes else (
        round(value_change / investment * 100, 2) if investment else ZERO
    )
    return render(request, 'users/dashboard.html', {
        'page_title': 'Dashboard | Stock Vault',
        'total_investment': str(investment),
        'total_sales': str(sales),
        'percentage_change': percentage,
        'profit_loss': None if missing_quotes else money(value_change),
        'missing_quotes': missing_quotes,
        'data_per_company_sector': sectors,
    })


@ratelimit(key='ip', rate='100/m', block=True)
@login_required(login_url='login')
def Portfolio(request):
    errors = []
    # Retain compatibility with older open forms, using the shared ledger.
    if request.method == 'POST':
        company = ListedCompanies.objects.filter(name__iexact=(request.POST.get('company') or '').strip()).first()
        try:
            if company is None:
                raise ValidationError('Choose a company from the current list.')
            record_transaction(
                user=request.user, company=company, transaction_type='buy',
                quantity=request.POST.get('share_quantity'),
                unit_price=request.POST.get('buying_rate'),
                purchase_type=request.POST.get('buy-type') or 'secondary',
            )
        except ValidationError as error:
            errors.extend(error.messages)
        else:
            return redirect('portfolio')
    datasets = []
    labels = {
        'previousClose': 'Previous Close', 'lastTradedPrice': 'Last Traded Price',
        'openPrice': 'Open Price', 'highPrice': 'High Price', 'lowPrice': 'Low Price',
        'closePrice': 'Close Price', 'fiftyTwoWeekHigh': '52 Week High',
        'fiftyTwoWeekLow': '52 Week Low',
    }
    recorded_trades = Transactions.objects.filter(
        user_id=request.user, company_id_id=OuterRef('company_id_id'), is_legacy=False,
    )
    holdings = Portfolios.objects.filter(user_id=request.user, number_of_shares__gt=0).annotate(
        has_trades=Exists(recorded_trades),
    ).select_related('company_id').order_by('company_id__name')
    for holding in holdings:
        company = holding.company_id
        data = {
            'company_id': company.pk, 'company_name': company.name,
            'company_sector': company.sector, 'tail': {}, 'when_to_sell': {},
            'can_remove': not holding.has_trades,
        }
        try:
            summary = holding_summary(holding)
            data.update(average_cost=summary['average_cost'], break_even_price=summary['break_even_price'])
        except ValidationError:
            data['cost_error'] = 'This opening balance needs an administrator’s correction.'
        data['when_to_sell'].update({
            'NUMBER OF SHARES': nepali_comma(holding.number_of_shares),
            'BOUGHT AT': holding.total_cost or ZERO,
        })
        quote = _market_quote(company)
        if quote is None:
            data['error'] = 'Market price is currently unavailable. Your recorded balance is shown below.'
        else:
            for key, label in labels.items():
                data['tail'][key] = (quote.get(key), label)
            try:
                previous = Decimal(str(quote.get('previousClose', 0)))
                price = Decimal(str(quote['lastTradedPrice']))
                if previous.is_finite() and previous > 0:
                    change = round((price - previous) / previous * 100, 2)
                    data['tail']['percentchange'] = (f'{change} %', 'Percent Change')
                estimate = sale_preview(quantity=holding.number_of_shares, total_cost=holding.total_cost or ZERO, selling_price=price)
                data['when_to_sell'].update({
                    'SOLD AT': estimate['gross_amount'],
                    'CASH IN HAND': estimate['net_amount'],
                    'PROFIT / LOSS': estimate['realized_gain'],
                    'SELLING FEES AND TAX': estimate['fees'] + estimate['capital_gains_tax'],
                })
                data['has_sale_estimate'] = True
            except (ValidationError, InvalidOperation, TypeError, ValueError):
                data['error'] = 'The market quote could not be used for a sale estimate.'
        datasets.append(data)
    return render(request, 'users/portfolio.html', {
        'page_title': 'Portfolio | Stock Vault', 'portfolio_datasets': datasets, 'errors': errors,
    })


@ratelimit(key='ip', rate='100/m', block=True)
@login_required(login_url='login')
@require_POST
def DeleteProtfolio(request):
    try:
        data = json.loads(request.body)
        company_id = data['company_id']
        if not isinstance(company_id, str) or not company_id:
            raise ValueError
    except (ValueError, TypeError, KeyError):
        return JsonResponse({'status': False, 'message': 'Invalid holding.'}, status=400)
    holding = Portfolios.objects.filter(user_id=request.user, company_id_id=company_id).first()
    if holding is None:
        return JsonResponse({'status': False, 'message': 'Holding not found.'}, status=404)
    try:
        delete_holding(holding)
    except ValidationError as error:
        return JsonResponse({'status': False, 'message': error.messages[0]}, status=409)
    return JsonResponse({'status': True, 'message': 'Opening holding removed.'})
