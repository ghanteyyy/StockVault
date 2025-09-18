from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from utils import utils


class ListedCompanies(models.Model):
    class Meta:
        verbose_name = _("Listed Companies")
        verbose_name_plural = _("Listed Companies")

    def __str__(self):
        return self.name

    id = models.CharField(primary_key=True, default=utils.generate_uuid_hex, max_length=255)

    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    abbreviation = models.CharField(verbose_name=_('abbreviation'), max_length=255, null=False, blank=False)
    logo = models.ImageField(verbose_name=('logo'), blank=True, null=True, upload_to=utils.company_logo_path)
    created_at = models.DateTimeField(editable=False, default=now)


class Portfolios(models.Model):
    class Meta:
        verbose_name = _("Share Holdings")
        verbose_name_plural = _("Share Holdings")

    def __str__(self):
        return self.company_id.name

    id = models.CharField(primary_key=True, default=utils.generate_uuid_hex, max_length=255)

    user_id = models.ForeignKey(to='Users.CustomUser', on_delete=models.CASCADE)
    company_id = models.ForeignKey(to="ListedCompanies", on_delete=models.CASCADE)

    total_cost = models.FloatField(blank=True, null=True)
    number_of_shares = models.IntegerField(blank=True, null=True, default=0)
    created_at = models.DateTimeField(verbose_name=_('created at'), default=now, editable=False)


class PortfolioLots(models.Model):
    class Meta:
        verbose_name = _("Share Holdings")
        verbose_name_plural = _("Share Holdings")

    def __str__(self):
        return self.company_id.name

    id = models.CharField(primary_key=True, default=utils.generate_uuid_hex, max_length=255)

    portfolio_id = models.ForeignKey(to="Portfolios", on_delete=models.CASCADE)

    total_cost = models.FloatField(blank=True, null=True)
    number_of_shares = models.IntegerField(blank=True, null=True, default=0)
    purchased_date = models.DateField(editable=False, default=now)


class Transactions(models.Model):
    class Meta:
        verbose_name = _("Transactions")
        verbose_name_plural = _("Transactions")

    def __str__(self):
        return self.company_id.name

    id = models.CharField(primary_key=True, default=utils.generate_uuid_hex, max_length=255)

    user_id = models.ForeignKey(to='Users.CustomUser', on_delete=models.CASCADE)
    company_id = models.ForeignKey(to="ListedCompanies", on_delete=models.CASCADE)

    number_of_shares = models.IntegerField(blank=True, null=True)
    transacted_price = models.FloatField(blank=True, null=True)
    transaction_date = models.DateField(editable=False, default=now)
    transaction_type = models.CharField(max_length=255, blank=True, null=True)


class WishLists(models.Model):
    class Meta:
        verbose_name = _("Wish Lists")
        verbose_name_plural = _("Wish Lists")

    def __str__(self):
        return self.company_id.name

    id = models.CharField(primary_key=True, default=utils.generate_uuid_hex, max_length=255)

    user_id = models.ForeignKey(to='Users.CustomUser', on_delete=models.CASCADE)
    company_id = models.ForeignKey(to="ListedCompanies", on_delete=models.CASCADE)


class FAQs(models.Model):
    class Meta:
        verbose_name = _("FAQs")
        verbose_name_plural = _("FAQs")

    id = models.CharField(primary_key=True, default=utils.generate_uuid_hex, max_length=255)

    question = models.CharField(max_length=255, blank=True, null=True)
    answer = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(
        verbose_name=_('created at'),
        default=now,
        editable=False,
    )


class StockMarketData(models.Model):
    id = models.CharField(primary_key=True, default=utils.generate_uuid_hex, max_length=255)

    trade_date   = models.DateField()
    ltp          = models.CharField(max_length=255)
    pct_change   = models.CharField(max_length=255)
    high         = models.CharField(max_length=255)
    low          = models.CharField(max_length=255)
    open_price   = models.CharField(max_length=255)
    qty          = models.CharField(max_length=255)
    turnover     = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    sector       = models.CharField(max_length=255)

    class Meta:
        db_table = "MarketData"
        managed = False


class NepseIndices(models.Model):
    id = models.CharField(primary_key=True, default=utils.generate_uuid_hex, max_length=255)

    date                = models.DateField()
    index_value         = models.CharField(max_length=255)
    absolute_change     = models.CharField(max_length=255)
    percentage_change   = models.CharField(max_length=255)

    class Meta:
        db_table = "NepseIndices"
        managed = False
