'''Audited management of share transactions and opening balances.'''

from decimal import Decimal
from uuid import uuid4

from django import forms
from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from Shares.models import ListedCompanies, Portfolios, Transactions
from Shares import trading
from utils.calculator import charges
from utils.utils import format_npr_amount
from .access import staff_required
from .utils import record_admin_action


class TransactionDetailsForm(forms.Form):
    transaction_type = forms.ChoiceField(choices=(('buy', 'Buy'), ('sell', 'Sell'), ('bonus', 'Bonus')))
    quantity = forms.IntegerField(min_value=1, max_value=trading.MAX_QUANTITY)
    unit_price = forms.DecimalField(min_value=Decimal('0'), max_digits=18, decimal_places=2, required=False)
    legacy_amount = forms.DecimalField(min_value=Decimal('0'), max_digits=20, decimal_places=2, required=False)
    purchase_type = forms.ChoiceField(choices=(('secondary', 'Secondary market'), ('ipo', 'IPO'), ('fpo', 'FPO'), ('right', 'Rights')), required=False)
    cgt_type = forms.ChoiceField(choices=tuple((key, key) for key in charges['capital_gains_tax']), required=False)
    transaction_date = forms.DateField()
    notes = forms.CharField(max_length=500, required=False)
    idempotency_key = forms.CharField(max_length=64, required=False)

    def clean_transaction_date(self):
        value = self.cleaned_data['transaction_date']

        if value > timezone.localdate():
            raise ValidationError('The transaction date cannot be in the future.')

        return value


class OpeningBalanceForm(forms.Form):
    quantity = forms.IntegerField(min_value=0, max_value=trading.MAX_QUANTITY)
    total_cost = forms.DecimalField(min_value=Decimal('0'), max_digits=20, decimal_places=2)

    def clean(self):
        values = super().clean()

        if values.get('quantity') == 0 and values.get('total_cost', 0) != 0:
            self.add_error('total_cost', 'An empty opening balance must have a zero cost.')

        return values


def management_options(kind):
    options = {
        'member_options': get_user_model().objects.order_by('email').values('pk', 'name', 'email'),
        'trade_company_options': ListedCompanies.objects.order_by('abbreviation', 'name').values('pk', 'name', 'abbreviation'),
    }
    if kind == 'transactions':
        options.update(
            today=timezone.localdate(),
            cgt_options=tuple(charges['capital_gains_tax']),
            default_cgt=trading.DEFAULT_CGT,
            trade_request_key=f'admin-{uuid4().hex}',
        )
    return options


def _error(message, errors=None, status=400):
    return JsonResponse({'status': False, 'message': message, 'errors': errors or {}}, status=status)


def _validation_error(error):
    errors = error.message_dict if hasattr(error, 'message_dict') else {}
    return _error(' '.join(error.messages), errors)


def _parties(request):
    user = get_user_model().objects.filter(pk=request.POST.get('user_id', '')).first()
    company = ListedCompanies.objects.filter(pk=request.POST.get('company_id', '')).first()
    errors = {}

    if user is None:
        errors['user_id'] = 'Choose an existing member.'

    if company is None:
        errors['company_id'] = 'Choose a company from the directory.'

    return user, company, errors


def _trade_values(form, legacy=False):
    values = form.cleaned_data.copy()
    values.pop('idempotency_key')

    if legacy:
        if values['legacy_amount'] is None:
            raise ValidationError({'legacy_amount': 'Enter the total value stored in this historical record.'})

        values.pop('unit_price', None)
        values.pop('purchase_type', None)
        values.pop('cgt_type', None)
        return values

    else:
        values.pop('legacy_amount', None)

        if values['transaction_type'] == 'bonus':
            values['unit_price'] = Decimal('0')

        elif values['unit_price'] is None or values['unit_price'] <= 0:
            raise ValidationError({'unit_price': 'Enter a price greater than zero.'})

    values['purchase_type'] = values.get('purchase_type') or 'secondary'
    values['cgt_type'] = values.get('cgt_type') or trading.DEFAULT_CGT

    return values


@staff_required
@require_POST
def AdminTransactionAdd(request):
    user, company, errors = _parties(request)
    form = TransactionDetailsForm(request.POST)

    if not form.is_valid() or errors:
        return _error('Check the transaction details.', {**form.errors, **errors})

    try:
        with transaction.atomic():
            entry = trading.record_transaction(
                user=user, company=company, idempotency_key=form.cleaned_data['idempotency_key'],
                **_trade_values(form),
            )
            existing_addition = LogEntry.objects.filter(
                content_type=ContentType.objects.get_for_model(Transactions),
                object_id=entry.pk, action_flag=ADDITION,
            ).exists()
            if not existing_addition:
                record_admin_action(
                    request, entry,
                    f'Recorded {entry.transaction_type} of {entry.number_of_shares} shares for {user.email}. Holdings recalculated.',
                    ADDITION,
                )

    except ValidationError as error:
        return _validation_error(error)

    return JsonResponse({'status': True, 'message': 'Transaction recorded and holding updated.'})


@staff_required
@require_POST
def AdminTransactionEdit(request):
    entry = Transactions.objects.select_related('user_id', 'company_id').filter(pk=request.POST.get('transaction_id', '')).first()

    if entry is None:
        return _error('This transaction could not be found.', status=404)

    if ((request.POST.get('user_id') and request.POST['user_id'] != str(entry.user_id_id))
            or (request.POST.get('company_id') and request.POST['company_id'] != str(entry.company_id_id))):
        return _error('The member and company of a transaction cannot be changed.')

    form = TransactionDetailsForm(request.POST)

    if not form.is_valid():
        return _error('Check the transaction details.', form.errors)

    try:
        with transaction.atomic():
            entry = trading.update_transaction(entry, **_trade_values(form, legacy=entry.is_legacy))
            detail = 'Updated historical record.' if entry.is_legacy else 'Recalculated the holding and later trades.'
            record_admin_action(request, entry, f'Edited transaction for {entry.user_id.email}. {detail}', CHANGE)

    except ValidationError as error:
        return _validation_error(error)

    return JsonResponse({'status': True, 'message': 'Transaction changes saved.'})


@staff_required
@require_POST
def AdminTransactionDelete(request):
    if request.POST.get('confirm') != 'yes':
        return _error('Confirm that you want to delete this transaction.')

    entry = Transactions.objects.select_related('user_id', 'company_id').filter(pk=request.POST.get('transaction_id', '')).first()

    if entry is None:
        return _error('This transaction could not be found.', status=404)

    try:
        with transaction.atomic():
            detail = 'Removed historical record.' if entry.is_legacy else 'Recalculated the holding and later trades.'
            record_admin_action(request, entry, f'Deleted transaction for {entry.user_id.email}. {detail}', DELETION)
            trading.delete_transaction(entry)

    except ValidationError as error:
        return _validation_error(error)

    return JsonResponse({'status': True, 'message': 'Transaction deleted.'})


@staff_required
@require_POST
def AdminHoldingSave(request):
    holding_id = request.POST.get('holding_id', '')
    holding = Portfolios.objects.select_related('user_id', 'company_id').filter(pk=holding_id).first() if holding_id else None

    if holding_id and holding is None:
        return _error('This holding could not be found.', status=404)

    if holding:
        user, company, errors = holding.user_id, holding.company_id, {}
        if ((request.POST.get('user_id') and request.POST['user_id'] != str(user.pk))
                or (request.POST.get('company_id') and request.POST['company_id'] != str(company.pk))):
            return _error('The member and company of a holding cannot be changed.')

    else:
        user, company, errors = _parties(request)

    form = OpeningBalanceForm(request.POST)

    if not form.is_valid() or errors:
        return _error('Check the opening balance.', {**form.errors, **errors})

    try:
        with transaction.atomic():
            saved = trading.set_opening_balance(
                user=user, company=company, holding_id=holding_id or None,
                create_only=not holding_id, **form.cleaned_data,
            )
            action = CHANGE if holding else ADDITION
            total_cost = format_npr_amount(form.cleaned_data['total_cost'])
            record_admin_action(
                request, saved,
                f'Set opening balance for {user.email} to {form.cleaned_data["quantity"]} shares '
                f'at a total cost of NPR {total_cost}. Later trades recalculated.',
                action,
            )

    except ValidationError as error:
        return _validation_error(error)

    return JsonResponse({'status': True, 'message': 'Opening balance saved and holding recalculated.'})


@staff_required
@require_POST
def AdminHoldingDelete(request):
    if request.POST.get('confirm') != 'yes':
        return _error('Confirm that you want to remove this opening holding.')

    holding = Portfolios.objects.select_related('user_id', 'company_id').filter(pk=request.POST.get('holding_id', '')).first()

    if holding is None:
        return _error('This holding could not be found.', status=404)

    try:
        with transaction.atomic():
            record_admin_action(request, holding, f'Removed opening holding for {holding.user_id.email}. Historical transactions retained.', DELETION)
            trading.delete_holding(holding)

    except ValidationError as error:
        return _validation_error(error)

    return JsonResponse({'status': True, 'message': 'Opening holding removed. Historical transactions are retained.'})
