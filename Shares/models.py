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


class ShareHoldings(models.Model):
    class Meta:
        verbose_name = _("Share Holdings")
        verbose_name_plural = _("Share Holdings")

    def __str__(self):
        return self.company_id.name

    id = models.CharField(primary_key=True, default=utils.generate_uuid_hex, max_length=255)

    user_id = models.ForeignKey(to='Users.CustomUser', on_delete=models.CASCADE)
    company_id = models.ForeignKey(to="ListedCompanies", on_delete=models.CASCADE)

    quantity = models.IntegerField(blank=True, null=True)
    price_per_share = models.FloatField(blank=True, null=True)
    bonus_quantity = models.IntegerField(blank=True, null=True, default=0)

    purchased_date = models.DateTimeField(editable=False, default=now)


class WishLists(models.Model):
    class Meta:
        verbose_name = _("Wish Lists")
        verbose_name_plural = _("Wish Lists")

    def __str__(self):
        return self.company_id.name

    id = models.CharField(primary_key=True, default=utils.generate_uuid_hex, max_length=255)

    user_id = models.ForeignKey(to='Users.CustomUser', on_delete=models.CASCADE)
    company_id = models.ForeignKey(to="ListedCompanies", on_delete=models.CASCADE)


class HistoricalPrices(models.Model):
    class Meta:
        verbose_name = _("Historical Prices")
        verbose_name_plural = _("Historical Prices")

    def __str__(self):
        return self.company_id.name

    id = models.CharField(primary_key=True, default=utils.generate_uuid_hex, max_length=255)
    company_id = models.ForeignKey(to='ListedCompanies', on_delete=models.CASCADE)

    opening_price = models.IntegerField(blank=True, null=True)
    closing_price = models.IntegerField(blank=True, null=True)

    recorded_at = models.DateTimeField(editable=False, default=now)


class RecentActivities(models.Model):
    id = models.CharField(primary_key=True, editable=False, default=utils.generate_uuid_hex, max_length=255)
    user_id = models.ForeignKey('Users.CustomUser', on_delete=models.CASCADE)
    company_id = models.ForeignKey('Shares.ListedCompanies', on_delete=models.CASCADE)

    activity = models.TextField(editable=False)
    recorded_at = models.DateTimeField(editable=False, default=now)
