from django.utils.timezone import now as timezone_now
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
import Users.models as user_models
import Shares.models as share_models


@login_required(login_url='login')
def AdminPage(request):
    total_users = user_models.CustomUser.objects.count()
    total_transactions = share_models.Transactions.objects.filter(transaction_date__month=timezone_now().month).count()
    total_transacted_price = share_models.Transactions.objects.filter(
                                    transaction_date__month=timezone_now().month,
                                    transaction_date__year=timezone_now().year).aggregate(total=Coalesce(Sum('transacted_price'), Value(0.0)))['total']

    context = {
        'page_title': 'Admin | Stock Vault',
        'total_users': format(total_users, ','),
        'total_transactions': format(total_transactions, ','),
        'total_transacted_price': format(total_transacted_price, ',')
    }

    return render(request, 'admin/dashboard.html', context)
