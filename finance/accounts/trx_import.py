import csv
import datetime

from decimal import Decimal
from django.db.models import Q
from finance.accounts.models import Transaction


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

    def __init__(self, main_account_pk, filename, *args, **kwargs):
        self.main_account_pk = main_account_pk
        self.filename = filename
        self.transactions = []

    def parse_file(self):
        """Parse file and create transactions"""
        with open(self.filename, 'rb') as fp:
            filereader = csv.DictReader(fp, delimiter=',')
            for trx_import in filereader:
                trx = self.map_fields(trx_import)
                self.set_accounts(trx)
                trx['DELETE'] = self.is_duplicate(trx)
                self.transactions.append(trx)

    def map_fields(self, trx_import):
        """Map the respecitve fields"""
        if 'Post Date' in trx_import.keys():
            return {
                'date': datetime.datetime.strptime(trx_import['Post Date'],
                                                   "%m/%d/%Y"),
                'summary': trx_import['Description'],
                'amount': trx_import['Amount'],
            }
        elif 'BANK ID' in trx_import.keys():
            return {
                'date': datetime.datetime.strptime(
                    trx_import['Transaction Date'], "%Y-%m-%d"
                ),
                'summary': trx_import[' Transaction Description'],
                'amount': trx_import['Transaction Amount']
            }
        else:
            raise 'Unknown file format'

    def set_accounts(self, trx):
        """Set debit/credit accounts for transaction"""
        other_account_id = self.get_account(trx['summary'])
        if Decimal(trx['amount']) < 0:
            trx['account_credit'] = self.main_account_pk
            trx['account_debit'] = other_account_id
        else:
            trx['account_debit'] = self.main_account_pk
            trx['account_credit'] = other_account_id
        trx['amount'] = str(abs(Decimal(trx['amount'])))

    def get_account(self, summary):
        """Look for other side of transaction based on description"""
        res = Transaction.objects.filter(summary=summary).filter(
            Q(account_debit__pk=self.main_account_pk) |
            Q(account_credit__pk=self.main_account_pk)
        ).first()
        if res is None:
            return None
        if res.account_debit.pk == self.main_account_pk:
            return res.account_credit.pk
        return res.account_debit.pk

    def is_duplicate(self, trx):
        """Check whether transaction is a possible duplicate"""
        return bool(Transaction.objects.filter(
            summary=trx['summary'],
            amount=trx['amount'],
            date=trx['date']
        ).first())
