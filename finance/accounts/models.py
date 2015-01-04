from django.db import models
from django.db.models import Q, Sum
from finance.core.models import Profile


class AccountType(models.Model):
    TYPE_CHOICES = (
        ("DEBIT", "Debit"),
        ("CREDIT", "Credit"),
    )
    name = models.CharField(max_length=20)
    default_type = models.CharField(max_length=20, choices=TYPE_CHOICES,
                                    default="DEBIT")
    profile = models.ForeignKey(Profile)

    class Meta:
        ordering = ["name"]
        unique_together = (("name", "profile"), )

    # TODO add method that indicates accounts associated with
    # remove delete link in list if accounts associated

    def __unicode__(self):
        return self.name


class Account(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250, blank=True)
    account_type = models.ForeignKey(AccountType)
    profile = models.ForeignKey(Profile)
    parent = models.ForeignKey('Account', null=True, blank=True,
                               limit_choices_to={"is_category": True})
    is_category = models.BooleanField(default=False)

    class Meta:
        ordering = ["account_type", "name"]

    def __unicode__(self):
        return self.name

    def balance(self):
        """Current balance of account"""
        balance = 0
        if self.is_category:
            for acct in self.subaccounts():
                balance += acct.balance()
        else:
            debit_total = self.debit.all().aggregate(
                total=Sum("amount")
            )["total"]
            credit_total = self.credit.all().aggregate(
                total=Sum("amount")
            )["total"]
            balance += debit_total if debit_total is not None else 0
            balance -= credit_total if credit_total is not None else 0
        return balance

    def subaccounts(self):
        return Account.objects.filter(parent=self)

    def transactions(self):
        """Get all transactions associated with this account

        We want to clearly indicate the opposite account
        And maintain a running balance for each transaction
        """
        trxs = Transaction.objects.filter(
            Q(account_debit=self) | Q(account_credit=self)
        ).order_by("date")
        trx_list = []
        balance = 0
        for trx in trxs:
            # remove duplicate information
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
        # TODO determine account debit and then show amount in
        # negative or positive
        # or think of a better short description of transaction to show
        return u"{summary} {amount}".format(
            summary=self.summary,
            amount=self.amount
        )


