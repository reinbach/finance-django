import csv
import datetime

from decimal import Decimal
from django.db import models
from django.db.models import Q
from finance.core.models import Profile


class AccountType(models.Model):
    name = models.CharField(max_length=20)
    profile = models.ForeignKey(Profile)

    class Meta:
        ordering = ["name"]
        unique_together = (("name", "profile"), )

    # TODO add method that indicates accounts associated with
    # remove delete link in list if accounts associated

    def __unicode__(self):
        return self.name


class Account(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=250, blank=True)
    account_type = models.ForeignKey(AccountType)
    profile = models.ForeignKey(Profile)

    def __unicode__(self):
        return self.name

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
    account_debit = models.ForeignKey(Account, related_name="debit",
                                      verbose_name="debit")
    account_credit = models.ForeignKey(Account, related_name="credit",
                                       verbose_name="credit")
    amount = models.DecimalField(decimal_places=2, max_digits=8)
    summary = models.CharField(max_length=50)
    description = models.CharField(max_length=250, blank=True)
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


class TransactionsImport():
    """Import transactions from csv file

    Expected format of file:
    Type, Trans Date, Post Date, Description, Amount

    Need to know which account these transactions are against.

    For each transaction in the file do;
    1. Does similar record exist in system?
     - does a record exist where summary equals description?
     - if so, use that same account for the other side of the transaction
    2. Is this transaction a duplicate?
     - does a record exist with the same post date and amount
     - mark as duplicate
    """

    def __init__(self, main_account_id, filename, *args, **kwargs):
        self.main_account_id = main_account_id
        self.filename = filename
        self.transactions = []

    def parse_file(self):
        """Parse file and create transactions"""
        with open(self.filename, 'rb') as fp:
            filereader = csv.DictReader(fp, delimiter=',')
            for trx_import in filereader:
                trx = self.map_fields(trx_import)
                self.set_accounts(trx)
                trx['duplicate'] = self.is_duplicate(trx)
                self.transactions.append(trx)

    def map_fields(self, trx_import):
        """Map the respecitve fields"""
        return {
            'date': trx_import['Post Date'],
            'summary': trx_import['Description'],
            'amount': trx_import['Amount'],
        }

    def set_accounts(self, trx):
        """Set debit/credit accounts for transaction"""
        other_account_id = self.get_account(trx['summary'])
        if Decimal(trx['amount']) < 0:
            trx['credit'] = self.main_account_id
            trx['debit'] = other_account_id
        else:
            trx['debit'] = self.main_account_id
            trx['credit'] = other_account_id
        trx['amount'] = str(abs(Decimal(trx['amount'])))

    def get_account(self, summary):
        """Look for other side of transaction based on description"""
        res = Transaction().query.filter(
            Transaction.summary == summary).first()

        if res is None:
            return None

        if res.account_debit_id == self.main_account_id:
            return res.account_credit_id
        return res.account_debit_id

    def is_duplicate(self, trx):
        """Check whether transaction is a possible duplicate"""
        return bool(Transaction.query.filter(
            Transaction.summary == trx['summary'],
            Transaction.amount == trx['amount'],
            Transaction.date == datetime.datetime.strptime(
                trx['date'], "%m/%d/%Y"
            ).strftime("%Y-%m-%d")
        ).first())
