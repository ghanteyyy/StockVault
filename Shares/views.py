from django.shortcuts import render
from . import models as share_models


def modify_shares(user, company_name, quantity, rate, mode):
    """
    Update a user's share holdings by buying or selling shares of a specified company.

    Args:
        user (User): The user performing the transaction.
        company_name (str): The name of the company whose shares are being transacted.
        quantity (int or str): The number of shares to buy or sell.
        rate (float or str): The price per share for the transaction.
        mode (str): The transaction type, either 'buy' or 'sell'.

    Behavior:
        - For 'buy', increases the user's number of shares and total cost for the company.
        - For 'sell', decreases the user's number of shares and total cost for the company.
        - If the user has no existing holding for the company, creates a new Portfolios record.
        - If selling results in zero or negative shares, deletes the holding.
        - Logs the transaction in RecentActivities.

    Example:
        modify_shares(request.user, "Apple Inc.", 10, 150.0, "buy")
        modify_shares(request.user, "Apple Inc.", 5, 155.0, "sell")
    """

    rate = float(rate)
    quantity = int(quantity)
    cost = quantity * rate

    cost = cost if mode == 'buy' else -cost
    quantity = quantity if mode == 'buy' else -quantity

    action_type = 'Bought' if mode == 'buy' else 'Sold'

    company = share_models.ListedCompanies.objects.get(name=company_name)

    if share_models.Portfolios.objects.filter(user_id=user, company_id=company).exists():
        share_holding = share_models.Portfolios.objects.get(user_id=user, company_id=company)
        share_holding.number_of_shares += quantity
        share_holding.total_cost += cost

        if share_holding.number_of_shares <= 0:
            share_holding.delete()

        else:
            share_holding.save()

    else:
        # Create a new share holding if it doesn't exist
        share_models.Portfolios.objects.create(user_id=user, company_id=company, number_of_shares=quantity, total_cost=quantity * rate)

    share_models.Transactions.objects.create(user_id=user, company_id=company, number_of_shares=abs(quantity), transacted_price=abs(cost), transaction_type=mode)
