"""Compatibility entry point for callers that record share movements."""
from django.core.exceptions import ValidationError

from Shares.models import ListedCompanies
from Shares.trading import record_transaction


def modify_shares(user, company_name, quantity, rate, mode):
    company = ListedCompanies.objects.filter(name__iexact=company_name).first()
    if company is None:
        raise ValidationError('Choose a listed company.')
    return record_transaction(
        user=user, company=company, transaction_type=mode,
        quantity=quantity, unit_price=rate,
    )
