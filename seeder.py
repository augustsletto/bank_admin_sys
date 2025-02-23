
def seedData():
    fake = Faker()
    list_of_account_types = list(AccountType)

    customers_to_add = []
    accounts_to_add = []
    transactions_to_add = []

    number_of_customers_in_db = Customer.query.count()

    while number_of_customers_in_db < MAX_NR_OF_CUSTOMERS:
        new_customer = Customer(
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
        customers_to_add.append(new_customer)
        number_of_customers_in_db += 1

    # 🚀 **Bulk insert customers** to DB
    db.session.bulk_save_objects(customers_to_add)
    db.session.commit()
    print(f"✅ Inserted {len(customers_to_add)} customers")

    # Fetch all inserted customers with IDs
    all_customers = Customer.query.all()

    for customer in all_customers:
        number_of_accounts = random.randint(MINIMUM_NR_OF_ACCOUNTS, MAX_NR_OF_ACCOUNTS)

        for _ in range(number_of_accounts):
            account_type = random.choice(list_of_account_types)
            account_created_at = datetime.now() - timedelta(days=random.randint(365, 3650))

            new_account = Account(
                account_type=account_type,
                created=account_created_at,
                balance=Decimal('0.00'),
                customer_id=customer.id
            )
            accounts_to_add.append(new_account)

    # 🚀 **Bulk insert accounts** to DB
    db.session.bulk_save_objects(accounts_to_add)
    db.session.commit()
    print(f"✅ Inserted {len(accounts_to_add)} accounts")

    # Fetch all inserted accounts with IDs
    all_accounts = Account.query.all()

    for account in all_accounts:
        number_of_transactions = random.randint(MINIMUM_NR_OF_TRANSACTIONS, MAX_NR_OF_TRANSACTIONS)
        start_date = account.created

        for _ in range(number_of_transactions):
            trans_amount = Decimal(random.randint(0, 30) * 100)
            fake_transaction_date = fake.date_time_between_dates(
                datetime_start=start_date, datetime_end=start_date + timedelta(days=10))

            new_transaction = Transaction(
                type=TransactionType.DEBIT if random.randint(0, 100) > 70 else TransactionType.CREDIT,
                operation=random.choice(list(TransactionOperation)),
                date=fake_transaction_date,
                amount=trans_amount,
                new_balance=account.balance + trans_amount if random.randint(0, 100) > 50 else account.balance - trans_amount,
                account_id=account.id
            )

            transactions_to_add.append(new_transaction)
            start_date += timedelta(days=1)

    # 🚀 **Bulk insert transactions** to DB
    db.session.bulk_save_objects(transactions_to_add)
    db.session.commit()
    print(f"✅ Inserted {len(transactions_to_add)} transactions")

    print(f"🎉 Seeding complete: {MAX_NR_OF_CUSTOMERS} customers, {len(accounts_to_add)} accounts, {len(transactions_to_add)} transactions.")