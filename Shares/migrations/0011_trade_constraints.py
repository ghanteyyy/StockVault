
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "Shares",
            "0010_trade_ledger",
        ),
    ]

    operations = [

        # Each user can have only one aggregate holding
        # per company.
        migrations.AddConstraint(
            model_name="portfolios",
            constraint=models.UniqueConstraint(
                fields=(
                    "user_id",
                    "company_id",
                ),
                name="unique_user_company_holding",
            ),
        ),

        # Prevent duplicate trade requests for a user
        # when the same non-null idempotency key is reused.
        migrations.AddConstraint(
            model_name="transactions",
            constraint=models.UniqueConstraint(
                fields=(
                    "user_id",
                    "idempotency_key",
                ),
                name="unique_user_trade_request",
            ),
        ),
    ]
