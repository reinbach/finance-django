from django.db import models


class AccountType(models.Model):
    name = models.CharField(max_length="20", unique=True)

    def __unicode__(self):
        return self.name

    def jsonify(self):
        return {
            'account_type_id': self.account_type_id,
            'name': self.name,
        }


class Account(models.Model):
    name = models.CharField(max_length="50", unique=True)
    description = models.CharField(max_length="250")
    account_type = models.ForeignKey(AccountType)

    def __unicode__(self):
        return u"{name} [{account_type}]".format(
            name=self.name,
            account_type=self.account_type.name
        )

    def jsonify(self):
        if self.account_type is None:
            account_type_id = None
        else:
            account_type_id = self.account_type.account_type_id
        res = {
            'account_id': self.account_id,
            'name': self.name,
            'account_type_id': account_type_id,
            'description': self.description,
            'balance': self.get_balance(),
        }

        if self.account_type is not None:
            res['account_type'] = self.account_type.jsonify()

        return res

    def get_total(self, trx_list):
        """Get the sum of the relevant transactions"""
        total = 0
        for trx in trx_list:
            total += trx.amount
        return total

    def get_balance(self):
        """Current balance of account"""
        balance = self.get_total(self.debits) - self.get_total(self.credits)
        return balance

    def transactions(self):
        """Get all transactions associated with this account

        We want to clearly indicate the opposite account
        And maintain a running balance for each transaction
        """
        trx_list = list(self.debits) + list(self.credits)
        balance = 0
        for trx in trx_list:
            # remove duplicate information
            if self.account_id == trx.account_debit.account_id:
                balance += trx.amount
            else:
                balance -= trx.amount
            trx.balance = balance
        return trx_list


class Transaction(models.Model):
    account_debit = models.ForeignKey(Account, related_name="debit")
    account_credit = models.ForeignKey(Account, related_name="credit")
    amount = models.DecimalField(decimal_places=2, max_digits=8)
    summary = models.CharField(max_length="50")
    description = models.CharField(max_length="250")
    date = models.DateField()

    def __unicode__(self):
        #TODO determine account debit and then show amount in
        # negative or positive
        # or think of a better short description of transaction to show
        return u"summary {amount}".format(
            summary=self.summary,
            amount=self.amount
        )

    def jsonify(self):
        debit = getattr(self.account_debit, 'account_id', None)
        credit = getattr(self.account_credit, 'account_id', None)
        res = {
            'transaction_id': self.transaction_id,
            'account_debit_id': debit,
            'account_credit_id': credit,
            'amount': self.amount,
            'summary': self.summary,
            'description': self.description,
            'date': self.date.strftime("%Y-%m-%d")
        }

        if self.account_debit is not None:
            res['debit'] = self.account_debit.jsonify()

        if self.account_credit is not None:
            res['credit'] = self.account_credit.jsonify()

        # balance may be set as a running total for an account
        if hasattr(self, 'balance'):
            res['balance'] = self.balance

        return res
