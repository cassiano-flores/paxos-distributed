class Account:
    def __init__(self):
        self.balance = 0

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            return True
        return False

    def get_balance(self):
        return self.balance


class Bank:
    def __init__(self):
        self.accounts = {}

    def get_account(self, account_id):
        if account_id not in self.accounts:
            print(f"Account doesn't exist. Creating account {account_id}...")
            self.accounts[account_id] = Account()
        return self.accounts[account_id]

    def deposit(self, account_id, amount):
        account = self.get_account(account_id)
        account.deposit(amount)

    def withdraw(self, account_id, amount):
        account = self.get_account(account_id)
        return account.withdraw(amount)

    def transfer(self, from_account_id, to_account_id, amount):
        from_account = self.get_account(from_account_id)
        to_account = self.get_account(to_account_id)
        if from_account.withdraw(amount):
            to_account.deposit(amount)
            return True
        return False

    def get_balance(self, account_id):
        account = self.get_account(account_id)
        return account.get_balance()
