import csv
import datetime
import os
import subprocess

from decimal import Decimal
from django.db.models import Q
from finance.accounts.models import Transaction


class TransactionsImport():
    """Import transactions from file

    Handle PDF, CSV file formats

    PDF:
    If PDF, convert to text and then extract trxs from
    lines in expected format

    CSV:
    Format of file may be one of the following:

    Type, Trans Date, Post Date, Description, Amount

    or

    BANK ID,Account Number,Account Type,Balance,Start Date,End Date,
    Transaction Type,Transaction Date,Transaction Amount,
    Transaction ID, Transaction Description


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
        self.year = kwargs.get("year", datetime.date.today().year)

    def get_file_type(self):
        filename, file_ext = os.path.splitext(self.filename)
        if ".pdf" == file_ext.lower():
            return "PDF"
        return "CSV"

    def parse_file(self):
        """Based on file ext, parse file and create transactions"""

        file_type = self.get_file_type()

        if file_type == "PDF":
            temp_filename, _ = os.path.splitext(self.filename)
            temp_file = "{0}.txt".format(temp_filename)
            subprocess.Popen(["pdftotext", "-layout", self.filename,
                              temp_file]).communicate()
            with open(temp_file, "rb") as fp:
                for row in fp:
                    try:
                        data = row.split(" " * 15)
                        month, day = data[0].split("/")
                        trx = {
                            "date": datetime.date(int(self.year), int(month),
                                                  int(day)),
                            "summary": data[1].strip(),
                            "amount": Decimal(data[-1].strip())
                        }
                        self.add_trx(trx)
                    except Exception:
                        pass
            os.unlink(temp_file)
        else:
            with open(self.filename, 'rb') as fp:
                filereader = csv.DictReader(fp, delimiter=',')
                for row in filereader:
                    trx = self.map_fields(row)
                    self.add_trx(trx)

    def add_trx(self, trx):
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
            raise Exception('Unknown file format')

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
