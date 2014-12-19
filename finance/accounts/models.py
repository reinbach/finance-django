from django.db import models
from django.db.models import Q
from finance.core.models import Profile


class AccountType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    profile = models.ForeignKey(Profile)

    def __unicode__(self):
        return self.name


class Account(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=250)
    account_type = models.ForeignKey(AccountType)
    profile = models.ForeignKey(Profile)

    def __unicode__(self):
        return u"{name} [{account_type}]".format(
            name=self.name,
            account_type=self.account_type.name
        )

    def get_total(self, trx_list):
        """Get the sum of the relevant transactions"""
        total = 0
        for trx in trx_list:
            total += trx.amount
        return total

    @property
    def balance(self):
        """Current balance of account"""
        balance = self.get_total(self.debit.all()) - self.get_total(
            self.credit.all())
        return balance

    def transactions(self):
        """Get all transactions associated with this account

        We want to clearly indicate the opposite account
        And maintain a running balance for each transaction
        """
        trxs = Transaction.objects.filter(Q(account_debit=self) |
                                          Q(account_credit=self))
        trx_list = []
        balance = 0
        for trx in trxs:
            # remove duplicate information
            if self == trx.account_debit:
                balance += trx.amount
            else:
                balance -= trx.amount
            trx_list.append((trx, balance))
        return trx_list


class Transaction(models.Model):
    account_debit = models.ForeignKey(Account, related_name="debit")
    account_credit = models.ForeignKey(Account, related_name="credit")
    amount = models.DecimalField(decimal_places=2, max_digits=8)
    summary = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    date = models.DateField()

    class Meta:
        ordering = ["date", ]

    def __unicode__(self):
        # TODO determine account debit and then show amount in
        # negative or positive
        # or think of a better short description of transaction to show
        return u"{summary} {amount}".format(
            summary=self.summary,
            amount=self.amount
        )
