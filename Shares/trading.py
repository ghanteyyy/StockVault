"""Aggregate holdings and a replayable, weighted-average transaction ledger.

Historical rows predate reliable unit-price/cost-basis data. They remain a
separate history, while an explicit opening balance preserves existing shares.
"""
import datetime
import re
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from django.utils import timezone

from Shares.models import ListedCompanies, Portfolios, Transactions
from utils import calculator


D = Decimal
ZERO = D('0.00')
CENT = D('0.01')
MAX_MONEY = D('999999999999999999.99')
MAX_PRICE = D('9999999999999999.99')
MAX_QUANTITY = 2147483647
DEFAULT_CGT = '365 days or less (5%)'
TRANSACTION_TYPES = ('buy', 'sell', 'bonus')
PURCHASE_TYPES = ('secondary', 'ipo', 'fpo', 'right')


def _money(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _decimal(value, label, *, positive=False, maximum=MAX_MONEY):
    try:
        result = D(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError(f'{label} must be a valid number.')
    if not result.is_finite() or result < 0 or result > maximum:
        raise ValidationError(f'{label} must be a finite, non-negative amount within the supported range.')
    if positive and result <= 0:
        raise ValidationError(f'{label} must be greater than zero.')
    if result != _money(result):
        raise ValidationError(f'{label} can have at most two decimal places.')
    return _money(result)


def _quantity(value, *, allow_zero=False):
    try:
        result = D(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError('Number of shares must be a whole number.')
    minimum = 0 if allow_zero else 1
    if not result.is_finite() or result != result.to_integral_value() or result < minimum or result > MAX_QUANTITY:
        raise ValidationError(f'Number of shares must be a whole number between {minimum} and {MAX_QUANTITY:,}.')
    return int(result)


def _date(value):
    if value in (None, ''):
        result = timezone.localdate()
    elif isinstance(value, datetime.datetime):
        result = value.date()
    elif isinstance(value, datetime.date):
        result = value
    else:
        try:
            result = datetime.date.fromisoformat(str(value))
        except (ValueError, TypeError):
            raise ValidationError('Enter a valid transaction date.')
    if result > timezone.localdate():
        raise ValidationError('Transaction date cannot be in the future.')
    return result


def _schedule():
    return {
        'minimum_brokerage': str(calculator.charges['broker']['min_brokerage']),
        'slabs': [[str(limit), str(rate)] for limit, rate in calculator.charges['broker']['slabs']],
        'sebon_rate': str(calculator.charges['sebon_fee_rate']),
        'dp_charge': str(calculator.charges['dp_charge']),
        'capital_gains_tax': {key: str(rate) for key, rate in calculator.charges['capital_gains_tax'].items()},
    }


def _charges(amount, schedule=None):
    schedule = schedule or _schedule()
    for limit, rate in schedule['slabs']:
        if amount <= D(limit):
            brokerage = _money(max(amount * D(rate), D(schedule['minimum_brokerage'])))
            break
    else:
        raise ValidationError('The configured brokerage schedule does not cover this trade.')
    return {
        'brokerage': brokerage,
        'sebon_fee': _money(amount * D(schedule['sebon_rate'])),
        'dp_charge': _money(D(schedule['dp_charge'])),
    }


def sale_preview(*, quantity, total_cost, selling_price, cgt_type=DEFAULT_CGT, fee_schedule=None):
    """Estimate a sale using an already allocated acquisition cost, once."""
    quantity = _quantity(quantity)
    cost = _decimal(total_cost, 'Cost basis')
    price = _decimal(selling_price, 'Selling price', positive=True, maximum=MAX_PRICE)
    schedule = fee_schedule or _schedule()
    if cgt_type not in schedule['capital_gains_tax']:
        raise ValidationError('Choose a valid capital gains tax category.')
    gross = _money(quantity * price)
    if gross > MAX_MONEY:
        raise ValidationError('The trade amount is too large.')
    charges = _charges(gross, schedule)
    fees = sum(charges.values(), ZERO)
    before_tax = gross - fees
    tax = _money(max(before_tax - cost, ZERO) * D(schedule['capital_gains_tax'][cgt_type]))
    net = _money(before_tax - tax)
    gain = _money(net - cost)
    return {
        'quantity': quantity,
        'gross_amount': gross,
        'fees': fees,
        'capital_gains_tax': tax,
        'net_amount': net,
        'cost_basis': cost,
        'realized_gain': gain,
        'gross_selling_amount': gross,
        'final_receivable_amount': net,
        'profit_after_tax': gain,
        'brokerage_commission': charges['brokerage'],
        'sebon_commission': charges['sebon_fee'],
        'dp_charge': charges['dp_charge'],
    }


def _break_even(quantity, cost, cgt_type):
    """Find the first qualifying penny, allowing for rounded fee steps."""
    schedule = _schedule()
    if cgt_type not in schedule['capital_gains_tax']:
        raise ValidationError('Choose a valid capital gains tax category.')
    sebon_rate = D(schedule['sebon_rate'])
    minimum_brokerage = D(schedule['minimum_brokerage'])
    dp_charge = _money(D(schedule['dp_charge']))
    price_ceiling = min(MAX_PRICE, (MAX_MONEY / quantity).quantize(CENT, rounding=ROUND_FLOOR))
    lower_gross = ZERO
    for limit, rate in schedule['slabs']:
        slab_limit = D(limit)
        # Brokerage and SEBON can each round down by half a penny. Start
        # at the first price that could break even under either fee formula.
        target = cost + dp_charge - CENT
        gross_floor = max(
            target / (1 - D(rate) - sebon_rate),
            (target + minimum_brokerage) / (1 - sebon_rate),
        )
        candidate = max(
            (lower_gross / quantity).quantize(CENT, rounding=ROUND_FLOOR) + CENT,
            (gross_floor / quantity).quantize(CENT, rounding=ROUND_CEILING),
        )
        maximum = price_ceiling
        if slab_limit.is_finite():
            maximum = min(maximum, (slab_limit / quantity).quantize(CENT, rounding=ROUND_FLOOR))
        while candidate <= maximum:
            gross = quantity * candidate
            proceeds_before_tax = gross - sum(_charges(gross, schedule).values(), ZERO)
            # Tax only applies to a gain and cannot turn it into a loss.
            if proceeds_before_tax >= cost:
                return candidate
            candidate += CENT
        lower_gross = slab_limit
    raise ValidationError('A break-even price could not be calculated within the supported range.')


def holding_summary(portfolio, quantity=None, cgt_type=DEFAULT_CGT):
    shares = _quantity(portfolio.number_of_shares or 0, allow_zero=True)
    cost = _decimal(portfolio.total_cost or ZERO, 'Holding cost')
    if shares == 0:
        if quantity not in (None, '', 0, '0'):
            raise ValidationError('There are no shares available to sell.')
        return {'quantity': 0, 'total_cost': cost, 'average_cost': ZERO, 'break_even_price': None, 'sell_quantity': 0, 'allocated_cost': ZERO}
    sell_quantity = shares if quantity in (None, '') else _quantity(quantity)
    if sell_quantity > shares:
        raise ValidationError(f'Only {shares:,} shares are available to sell.')
    allocated = cost if sell_quantity == shares else _money(cost * sell_quantity / shares)
    return {
        'quantity': shares,
        'total_cost': cost,
        'average_cost': _money(cost / shares),
        'break_even_price': _break_even(sell_quantity, allocated, cgt_type),
        'sell_quantity': sell_quantity,
        'allocated_cost': allocated,
    }


def _values(*, transaction_type, quantity, unit_price=0, purchase_type='secondary', cgt_type=DEFAULT_CGT, transaction_date=None, notes=''):
    kind = str(transaction_type or '').strip().lower()
    if kind not in TRANSACTION_TYPES:
        raise ValidationError('Choose buy, sell, or bonus shares.')
    quantity = _quantity(quantity)
    purchase_type = str(purchase_type or 'secondary').strip().lower()
    if purchase_type not in PURCHASE_TYPES:
        raise ValidationError('Choose a valid purchase type.')
    if cgt_type not in calculator.charges['capital_gains_tax']:
        raise ValidationError('Choose a valid capital gains tax category.')
    price = _decimal(unit_price, 'Price per share', positive=kind != 'bonus', maximum=MAX_PRICE)
    if kind == 'bonus' and price != ZERO:
        raise ValidationError('Bonus shares must have a zero purchase price.')
    if quantity * price > MAX_MONEY:
        raise ValidationError('The trade amount is too large.')
    notes = str(notes or '').strip()
    if len(notes) > 500:
        raise ValidationError('Notes must be at most 500 characters.')
    return {'transaction_type': kind, 'number_of_shares': quantity, 'unit_price': price, 'purchase_type': purchase_type, 'cgt_type': cgt_type, 'transaction_date': _date(transaction_date), 'notes': notes}


def _lock_user(user):
    user_id = getattr(user, 'pk', user)
    try:
        return get_user_model().objects.select_for_update().get(pk=user_id)
    except get_user_model().DoesNotExist:
        raise ValidationError('The selected member does not exist.')


def _company(company):
    try:
        return ListedCompanies.objects.select_for_update().get(pk=getattr(company, 'pk', company))
    except ListedCompanies.DoesNotExist:
        raise ValidationError('Choose a listed company.')


def _holding(user, company):
    holding, _created = Portfolios.objects.select_for_update().get_or_create(user_id=user, company_id=company, defaults={'number_of_shares': 0, 'total_cost': ZERO})
    if not holding.ledger_initialized:
        holding.opening_number_of_shares = _quantity(holding.number_of_shares or 0, allow_zero=True)
        holding.opening_total_cost = _decimal(holding.total_cost or ZERO, 'Opening cost')
        holding.ledger_initialized = True
        holding.save(update_fields=['opening_number_of_shares', 'opening_total_cost', 'ledger_initialized'])
    return holding


def _replay(holding):
    shares = _quantity(holding.opening_number_of_shares, allow_zero=True)
    cost = _decimal(holding.opening_total_cost, 'Opening cost')
    if shares == 0 and cost != ZERO:
        raise ValidationError('An opening balance with no shares must have zero cost.')
    entries = list(Transactions.objects.select_for_update().filter(user_id=holding.user_id, company_id=holding.company_id, is_legacy=False).order_by('transaction_date', 'created_at', 'id'))
    for entry in entries:
        quantity = entry.number_of_shares
        gross = _money(quantity * entry.unit_price)
        schedule = entry.fee_schedule or _schedule()
        fees = tax = basis = gain = ZERO
        if entry.transaction_type == 'buy':
            if entry.purchase_type == 'secondary':
                fees = sum(_charges(gross, schedule).values(), ZERO)
            net = _money(gross + fees)
            basis = net
            shares += quantity
            cost += net
        elif entry.transaction_type == 'bonus':
            if shares <= 0:
                raise ValidationError('Bonus shares require an existing holding on the transaction date.')
            shares += quantity
            gross = net = ZERO
        elif entry.transaction_type == 'sell':
            if quantity > shares:
                raise ValidationError(f'The sale on {entry.transaction_date:%Y-%m-%d} needs {quantity:,} shares, but only {shares:,} are available. Correct the transaction order or quantity.')
            basis = cost if quantity == shares else _money(cost * quantity / shares)
            sale = sale_preview(quantity=quantity, total_cost=basis, selling_price=entry.unit_price, cgt_type=entry.cgt_type, fee_schedule=schedule)
            fees, tax, net, gain = sale['fees'], sale['capital_gains_tax'], sale['net_amount'], sale['realized_gain']
            shares -= quantity
            cost = _money(cost - basis) if shares else ZERO
        else:
            raise ValidationError('A ledger entry has an unsupported transaction type.')
        if shares > MAX_QUANTITY or cost > MAX_MONEY:
            raise ValidationError('The resulting holding exceeds the supported range.')
        if abs(gain) > MAX_MONEY:
            raise ValidationError('The sale result is outside the supported range.')
        entry.gross_amount, entry.fees, entry.capital_gains_tax = gross, fees, tax
        entry.cost_basis, entry.net_amount, entry.realized_gain = basis, net, gain
        entry.balance_shares, entry.balance_cost = shares, _money(cost)
        entry.transacted_price = float(net)
    if entries:
        Transactions.objects.bulk_update(entries, ['gross_amount', 'fees', 'capital_gains_tax', 'cost_basis', 'net_amount', 'realized_gain', 'balance_shares', 'balance_cost', 'transacted_price'])
    holding.number_of_shares, holding.total_cost = shares, _money(cost)
    holding.save(update_fields=['number_of_shares', 'total_cost'])
    return holding


@db_transaction.atomic
def record_transaction(*, user, company, transaction_type, quantity, unit_price=0, purchase_type='secondary', cgt_type=DEFAULT_CGT, transaction_date=None, notes='', idempotency_key=None):
    values = _values(transaction_type=transaction_type, quantity=quantity, unit_price=unit_price, purchase_type=purchase_type, cgt_type=cgt_type, transaction_date=transaction_date, notes=notes)
    user = _lock_user(user)
    company = _company(company)
    key = str(idempotency_key or '').strip() or None
    if key and not re.fullmatch(r'[A-Za-z0-9_-]{8,64}', key):
        raise ValidationError('The transaction request identifier is invalid. Reload the form and try again.')
    if key:
        existing = Transactions.objects.filter(user_id=user, idempotency_key=key).first()
        if existing:
            if existing.company_id_id != company.pk or any(getattr(existing, name) != value for name, value in values.items()):
                raise ValidationError('This request identifier was already used for another transaction. Reload the form.')
            return existing
    holding = _holding(user, company)
    entry = Transactions.objects.create(user_id=user, company_id=company, idempotency_key=key, is_legacy=False, fee_schedule=_schedule(), **values)
    _replay(holding)
    entry.refresh_from_db()
    return entry


@db_transaction.atomic
def update_transaction(entry, **changes):
    """Edit a ledger row and replay it, or correct historical-only metadata."""
    entry_id = getattr(entry, 'pk', entry)
    try:
        current = Transactions.objects.get(pk=entry_id)
    except Transactions.DoesNotExist:
        raise ValidationError('The transaction no longer exists.')
    user = _lock_user(current.user_id_id)
    current = Transactions.objects.select_for_update().filter(pk=entry_id).first()
    if current is None:
        raise ValidationError('The transaction no longer exists.')
    for relation in ('user', 'company', 'user_id', 'company_id'):
        if relation in changes:
            raise ValidationError('The member and company of an existing transaction cannot be changed. Create a separate correction instead.')
    if current.is_legacy:
        allowed = {'transaction_type', 'quantity', 'transaction_date', 'notes', 'legacy_amount'}
        if set(changes) - allowed:
            raise ValidationError('Historical entries have no reliable unit price. Edit their recorded total amount only.')
        kind = str(changes.get('transaction_type', current.transaction_type) or '').strip().lower()
        if kind not in TRANSACTION_TYPES:
            raise ValidationError('Choose a valid transaction type.')
        current.transaction_type = kind
        current.number_of_shares = _quantity(changes.get('quantity', current.number_of_shares))
        current.transaction_date = _date(changes.get('transaction_date', current.transaction_date))
        current.transacted_price = float(_decimal(changes.get('legacy_amount', current.transacted_price or ZERO), 'Historical total amount'))
        current.notes = str(changes.get('notes', current.notes) or '').strip()
        if len(current.notes) > 500:
            raise ValidationError('Notes must be at most 500 characters.')
        current.save(update_fields=['transaction_type', 'number_of_shares', 'transaction_date', 'transacted_price', 'notes'])
        return current
    holding = _holding(user, current.company_id)
    allowed = {'transaction_type', 'quantity', 'unit_price', 'purchase_type', 'cgt_type', 'transaction_date', 'notes'}
    if set(changes) - allowed:
        raise ValidationError('Unsupported transaction fields.')
    values = _values(transaction_type=changes.get('transaction_type', current.transaction_type), quantity=changes.get('quantity', current.number_of_shares), unit_price=changes.get('unit_price', current.unit_price), purchase_type=changes.get('purchase_type', current.purchase_type), cgt_type=changes.get('cgt_type', current.cgt_type), transaction_date=changes.get('transaction_date', current.transaction_date), notes=changes.get('notes', current.notes))
    for name, value in values.items():
        setattr(current, name, value)
    current.save(update_fields=list(values))
    _replay(holding)
    current.refresh_from_db()
    return current


@db_transaction.atomic
def delete_transaction(entry):
    entry_id = getattr(entry, 'pk', entry)
    try:
        current = Transactions.objects.get(pk=entry_id)
    except Transactions.DoesNotExist:
        raise ValidationError('The transaction no longer exists.')
    user = _lock_user(current.user_id_id)
    current = Transactions.objects.select_for_update().filter(pk=entry_id).first()
    if current is None:
        raise ValidationError('The transaction no longer exists.')
    holding = None if current.is_legacy else _holding(user, current.company_id)
    current.delete()
    if holding:
        _replay(holding)


@db_transaction.atomic
def set_opening_balance(*, user, company, quantity, total_cost, create_only=False, holding_id=None):
    """Correct the imported starting balance, retaining every ledger entry."""
    shares = _quantity(quantity, allow_zero=True)
    cost = _decimal(total_cost, 'Opening cost')
    if shares == 0 and cost != ZERO:
        raise ValidationError('An opening balance with no shares must have zero cost.')
    user = _lock_user(user)
    company = _company(company)
    if create_only and Portfolios.objects.filter(user_id=user, company_id=company).exists():
        raise ValidationError('This member already has a holding for the selected company.')
    if holding_id is not None and not Portfolios.objects.filter(pk=holding_id, user_id=user, company_id=company).exists():
        raise ValidationError('The holding no longer exists.')
    holding = _holding(user, company)
    holding.opening_number_of_shares, holding.opening_total_cost = shares, cost
    holding.save(update_fields=['opening_number_of_shares', 'opening_total_cost'])
    return _replay(holding)


@db_transaction.atomic
def delete_holding(portfolio):
    holding_id = getattr(portfolio, 'pk', portfolio)
    try:
        current = Portfolios.objects.get(pk=holding_id)
    except Portfolios.DoesNotExist:
        raise ValidationError('The holding no longer exists.')
    _lock_user(current.user_id_id)
    current = Portfolios.objects.select_for_update().filter(pk=holding_id).first()
    if current is None:
        raise ValidationError('The holding no longer exists.')
    if Transactions.objects.filter(user_id=current.user_id, company_id=current.company_id, is_legacy=False).exists():
        raise ValidationError('This holding has recorded ledger activity. Correct its opening balance or transactions instead of deleting it.')
    current.delete()
