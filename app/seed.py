from faker import Faker
from decimal import Decimal
from datetime import datetime, timedelta
from .models import Role, User, Customer, Account, AccountType, Transaction, TransactionType, TransactionOperation
from .security import user_datastore
from flask_security import hash_password
import random


MAX_NR_OF_CUSTOMERS = 500
MAX_NR_OF_ACCOUNTS = 4
MINIMUM_NR_OF_ACCOUNTS = 1
MAX_NR_OF_TRANSACTIONS = 20
MINIMUM_NR_OF_TRANSACTIONS = 10



def seedData(db):

    
    if not Role.query.first():
        user_datastore.create_role(name="Admin", description="Administrator")
        user_datastore.create_role(name="Cashier", description="Cashier")
        db.session.commit()

    

    if not User.query.first():
        
        user_datastore.create_user(username="SebastianAdmin",email='sebastian.ohman@systementor.se', password=hash_password('Hejsan123#'), roles=['Admin','Cashier'])
        user_datastore.create_user(username="Sebastian",email='sebastian.ohman@teknikhögskolan.se', password=hash_password('Hejsan123#'), roles=['Cashier'])
        
        db.session.commit()
    
    
    
    fake = Faker()
    list_of_account_types = list(AccountType)

    number_of_customers_in_db =  Customer.query.count()
    while number_of_customers_in_db < MAX_NR_OF_CUSTOMERS:

        new_customer:Customer = Customer(
            given_name=fake.first_name(),
            surname=fake.last_name(),
            streetaddress=fake.street_address(),
            city=fake.city(),
            zipcode=fake.postcode(),
            country=fake.country(),
            country_code=fake.country_code(),
            birthday=fake.date_of_birth(),
            national_id=fake.ssn(),
            telephone_country_code=fake.country_calling_code(),
            telephone=fake.phone_number(),
            email_address=fake.email()
        )
        
        ## Create fake accounts for new customer
        number_of_accounts = random.randint(MINIMUM_NR_OF_ACCOUNTS, MAX_NR_OF_ACCOUNTS)
        
        for _ in range(number_of_accounts):
            account_type = random.choice(list_of_account_types)
            account_created_at = datetime.now() + timedelta(days=-random.randint(365,3650))        

            new_account:Account = Account(
                account_type=account_type,
                created = account_created_at,
                balance = Decimal('0.00'),
                customer_id=new_customer.id                
            )

            new_customer.accounts.append(new_account)

            ### Create fake transaktions for new account
            number_of_transactions = random.randint(MINIMUM_NR_OF_TRANSACTIONS, MAX_NR_OF_TRANSACTIONS)
            start_date = account_created_at

            for _ in range(number_of_transactions):
                new_transaction = Transaction()

                trans_amount = Decimal(random.randint(0,30)*100)
                new_transaction.amount = trans_amount

                fake_transaction_date = fake.date_time_between_dates(
                    datetime_start=start_date, datetime_end=start_date + timedelta(days=10))
                new_transaction.date = fake_transaction_date

                new_account.transactions.append(new_transaction)

                if new_account.balance - trans_amount < 0:
                    new_transaction.type = TransactionType.DEBIT
                else:
                    new_transaction.type = TransactionType.DEBIT if random.randint(0,100) > 70 else TransactionType.CREDIT

                random_roll = random.randint(0,100)
                if new_transaction.type == TransactionType.DEBIT:
                    new_account.balance += trans_amount

                    if random_roll < 20:
                        new_transaction.operation = TransactionOperation.DEPOSIT_CASH
                    elif random_roll < 66:
                        new_transaction.operation = TransactionOperation.SALARY
                    else:
                        new_transaction.operation = TransactionOperation.TRANSFER
                        
                else:
                    new_account.balance -= trans_amount

                    if random_roll < 40:
                        new_transaction.operation = TransactionOperation.ATM_WITHDRAWL
                    elif random_roll < 75:
                        new_transaction.operation = TransactionOperation.PAYMENT
                    elif random_roll < 85:
                        new_transaction.operation = TransactionOperation.BANK_WITHDRAWL
                    else:
                        new_transaction.operation = TransactionOperation.TRANSFER

                new_transaction.new_balance = new_account.balance
                start_date = fake_transaction_date
                    
            db.session.add(new_customer)
            db.session.commit()
            
            
            
            

        number_of_customers_in_db += 1