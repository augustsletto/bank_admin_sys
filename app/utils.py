from .models import db, Customer, Account, Transaction, TransactionOperation, TransactionType
from datetime import datetime, timedelta





# Get Country Data

def get_country_data(country_name=None):

    customer_query = db.session.query(Customer, db.func.sum(Account.balance).label("total_balance")).join(Account, Account.customer_id == Customer.id)
    total_customers_query = db.session.query(db.func.count(Customer.id))
    total_accounts_query = db.session.query(db.func.count(Account.id)).join(Customer, Customer.id == Account.customer_id)
    
    transactions_query = (
        db.session.query(Transaction, Customer.id, Customer.given_name, Customer.surname)
        .join(Account, Account.id == Transaction.account_id)
        .join(Customer, Customer.id == Account.customer_id)
    )
    
    if country_name and country_name.lower() != "all":
        customer_query = customer_query.filter(Customer.country == country_name)
        total_customers_query = total_customers_query.filter(Customer.country == country_name)
        total_accounts_query = total_accounts_query.filter(Customer.country == country_name)
        transactions_query = transactions_query.filter(Customer.country == country_name)
     
    customer_accounts = customer_query.group_by(Customer.id).order_by(db.desc("total_balance")).all()
    
    total_customers = total_customers_query.scalar()
    total_accounts = total_accounts_query.scalar()
    transactions = transactions_query.order_by(Transaction.date.desc()).all()
     
    richest_customers = []
    for customer, total_balance in customer_accounts:
        richest_customers.append({
            "name": f"{customer.given_name} {customer.surname}",
            "country": customer.country,
            "total_balance":total_balance

        })
         
    transaction_list = []
    for transaction, customer_id, given_name, surname in transactions:
        transaction_list.append({
            "id": transaction.id,
            "customer_id": customer_id,
            "customer_name":f"{given_name} {surname}",
            "type": transaction.type.name,
            "operation":transaction.operation.name,
            "date": transaction.date,
            "amount": float(transaction.amount),
            "new_balance": float(transaction.new_balance),
            "account_id":transaction.account_id
        }
        )
        
             
    return {
            "richest_customers": richest_customers,
            "total_customers": total_customers,
            "total_accounts": total_accounts,
            "transactions": transaction_list,
            }



# Transfer Money

def transfer_money(sender_account_id, receiver_account_id, amount):
    
    if amount <= 0:
        return False, "Invalid amount: Cannot transfer negative money."
    
    sender_account = db.session.get(Account, sender_account_id)
    receiver_account = db.session.get(Account, receiver_account_id)

    
    if not sender_account or not receiver_account:
        return False, "One or both accounts do not exist."
    
    if sender_account.id == receiver_account.id:
        return False, "Cannot transfer to the same account."
    
    if sender_account.balance < amount:
        return False, "Insufficient balance."
    
    if amount > 500000:
        return False, "Transaction amount exceeds the maximum transfer limit."
    
    
    is_internal_transfer = sender_account.customer_id == receiver_account.customer_id

    sender_transaction = Transaction(
        type=TransactionType.CREDIT,
        operation=TransactionOperation.TRANSFER,
        date=datetime.now(),
        amount=amount,
        new_balance=sender_account.balance - amount,
        account_id=sender_account.id
    )
    
    
    reciever_transaction = Transaction(
        type=TransactionType.DEBIT,
        operation=TransactionOperation.TRANSFER,
        date=datetime.now(),
        amount=amount,
        new_balance=receiver_account.balance + amount,
        account_id=receiver_account.id
    )


    sender_account.balance -= amount
    receiver_account.balance += amount
    
    db.session.add(sender_transaction)
    db.session.add(reciever_transaction)
    db.session.commit()
    
    return True, "Transfer successful!"

 
 
 
 
 # Filter/order customers
 
 
def get_filtered_customers(search_word):
    return Customer.query.filter(
        Customer.given_name.ilike(f"%{search_word}%") |
        Customer.surname.ilike(f"%{search_word}%") |
        Customer.streetaddress.ilike(f"%{search_word}%") |
        Customer.country.ilike(f"%{search_word}%") |
        Customer.city.ilike(f"%{search_word}%") |
        Customer.id.ilike(f"%{search_word}%") |
        Customer.national_id.ilike(f"%{search_word}%")
    )

def get_order_by_column(sort_column, sort_order):
    column = {
        "customer": Customer.given_name,
        "address": Customer.streetaddress,
        "city": Customer.city,
        "national_id": Customer.national_id,
        "id": Customer.id
    }.get(sort_column, Customer.id)
    
    return column.asc() if sort_order == "asc" else column.desc()




# Suspicious tracker


def detect_suspicious_transactions():
    suspicious_transactions = []
    three_days_ago = datetime.now() - timedelta(days=3)
    
    for customer in Customer.query.all():
        for account in customer.accounts:
            total_last_72h = db.session.query(db.func.sum(Transaction.amount))\
                .filter(Transaction.account_id == account.id, Transaction.date >= three_days_ago)\
                .scalar() or 0
            
            large_transactions = Transaction.query.filter(Transaction.account_id == account.id, Transaction.amount > 15000).all()
            
            if total_last_72h > 23000 or large_transactions:
                suspicious_transactions.append({
                    "customer_id": customer.id,
                    "customer_name": f"{customer.given_name} {customer.surname}",
                    "account_id": account.id,
                    "total_last_72h": float(total_last_72h),
                    "large_transactions": [t.id for t in large_transactions]
                })
    return suspicious_transactions


