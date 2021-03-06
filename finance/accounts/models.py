import datetime

from django.core.cache import cache
from django.db import models
from django.db.models import Q
from finance.core.models import Profile


class AccountTypeQuerySet(models.QuerySet):
    def yearly(self):
        return self.filter(yearly=True)

    def debits(self):
        return self.yearly().filter(default_type="DEBIT")

    def credits(self):
        return self.yearly().filter(default_type="CREDIT")


class AccountType(models.Model):
    TYPE_CHOICES = (
        ("DEBIT", "Debit"),
        ("CREDIT", "Credit"),
    )
    name = models.CharField(max_length=20)
    default_type = models.CharField(max_length=20, choices=TYPE_CHOICES,
                                    default="DEBIT")
    yearly = models.BooleanField(default=False)
    profile = models.ForeignKey(Profile)

    objects = AccountTypeQuerySet.as_manager()

    class Meta:
        ordering = ["name"]
        unique_together = (("name", "profile"), )

    def __unicode__(self):
        return self.name


class AccountQuerySet(models.QuerySet):
    def yearly(self):
        return self.filter(account_type__yearly=True)

    def clear_cache(self):
        for acct in self.yearly():
            acct.clear_cache()

    def debits(self):
        """Yearly accounts that are type DEBIT"""
        return self.yearly().filter(account_type__default_type="DEBIT")

    def credits(self):
        """Yearly accounts that are type CREDIT"""
        return self.yearly().filter(account_type__default_type="CREDIT")


class Account(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250, blank=True)
    account_type = models.ForeignKey(AccountType)
    profile = models.ForeignKey(Profile)
    parent = models.ForeignKey('Account', null=True, blank=True,
                               limit_choices_to={"is_category": True})
    is_category = models.BooleanField(default=False)

    objects = AccountQuerySet.as_manager()

    class Meta:
        ordering = ["account_type", "name"]

    def __unicode__(self):
        return self.name

    @property
    def cache_key(self):
        return "account-{0}".format(self.pk)

    def clear_cache(self):
        cache.delete(self.cache_key)

    def balance(self):
        """Current balance of account"""
        balance = cache.get(self.cache_key)
        if balance is not None:
            return balance
        balance = 0
        if self.is_category:
            for acct in self.subaccounts():
                balance += acct.balance()
        else:
            trxs = self.transactions()
            if trxs:
                balance = trxs[0].balance
        cache.set(self.cache_key, balance)
        return balance

    def subaccounts(self):
        return Account.objects.filter(parent=self)

    def transactions(self, month=None):
        """Get all transactions associated with this account

        We want to clearly indicate the opposite account
        And maintain a running balance for each transaction
        """
        year = self.profile.year
        trxs = Transaction.objects.filter(
            Q(account_debit=self) | Q(account_credit=self)
        ).filter(date__year=year)
        if month is not None:
            trxs = trxs.filter(date__month=month)
        trxs = trxs.order_by("date")
        trx_list = []
        balance = 0
        for trx in trxs:
            if self == trx.account_credit:
                trx.amount = trx.amount * -1
            balance += trx.amount
            trx.balance = balance
            trx_list.append(trx)
        return trx_list[::-1]


class Transaction(models.Model):
    account_debit = models.ForeignKey(Account, related_name="debit",
                                      verbose_name="debit")
    account_credit = models.ForeignKey(Account, related_name="credit",
                                       verbose_name="credit")
    amount = models.DecimalField(decimal_places=2, max_digits=8)
    summary = models.CharField(max_length=100)
    description = models.CharField(max_length=250, blank=True)
    date = models.DateField()

    class Meta:
        ordering = ["-date", ]

    def __unicode__(self):
        return u"{summary} {amount}".format(
            summary=self.summary,
            amount=self.amount
        )

    def save(self, **kwargs):
        super(Transaction, self).save(**kwargs)
        profile = self.account_debit.profile
        if isinstance(self.date, datetime.date):
            year = self.date.year
        else:
            year = self.date[:4]
        cache.delete_many([
            self.account_debit.cache_key,
            self.account_credit.cache_key,
            "{0}-{1}-debits-vs-credits".format(
                profile.pk,
                year
            ),
            "{0}-{1}-debits-vs-credits".format(
                profile.pk,
                year
            ),
        ])
