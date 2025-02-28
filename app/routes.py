
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_security import login_required, roles_required
from app.utils import get_country_data, transfer_money, get_filtered_customers, get_order_by_column
from app.forms import AddCustomerForm, AddAccountForm, EditCustomerForm, TransferForm
from datetime import datetime, timedelta, date
from .models import db, Customer, Account, Transaction, TransactionOperation, TransactionType, AccountType, Role, User, roles_users
import numpy as np
from collections import Counter
from sqlalchemy import  func


main_bp = Blueprint("main", __name__)


# Login route

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("User not found. Check your email.", "danger")
        elif not user.verify_password(password): 
            flash("Incorrect password. Please try again.", "danger")
        else:
            flash("Login successful!", "success")
            return redirect(url_for("main.startpage"))

    return render_template("security/login_user.html")

# Logout route
@main_bp.route('/logout')
@login_required
def logout():
    
    return redirect(url_for('main.logout'))




#Dashboard Route (index)

    
    
@main_bp.route("/", methods=["GET"])
@login_required
def startpage():
    
    
    
    country = request.args.get("country", "all")
    country_data = get_country_data(country)
    
    richest_customers_by_country = country_data["richest_customers"]
    total_customers_by_country = country_data["total_customers"]
    total_accounts_by_country = country_data["total_accounts"]
    transactions_by_country = country_data["transactions"]
    

    labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    balance_data_rich = [customer["total_balance"] for customer in country_data["richest_customers"]]
     
    main_bar_color =["#5641f5"]*11
    off_bar_color = ["#b5a3d9"]*11
    maxrange = np.arange(1, 11).tolist()
    

    transaction_data_operation = [t["operation"] for t in country_data["transactions"]]
    transaction_data_new_balance = [t["new_balance"] for t in country_data["transactions"]]
    transaction_by_date = [t["date"].weekday() for t in country_data["transactions"]]
    transaction_by_month = [t["date"].month for t in country_data["transactions"]]
    income_by_month = [t["operation"] for t in country_data["transactions"]]
    
    transaction_data_amount = [t["amount"] for t in country_data["transactions"]]
    country_list_items = sorted(set(db.session.execute(db.select(Customer.country)).scalars().all()))
    

    counter = Counter(transaction_by_date)
    iterations_per_week = dict(sorted(counter.items()))
    
    counter_month = Counter(transaction_by_month)
    iterations_per_month = dict(sorted(counter_month.items()))
    
    counter_income_by_month = Counter(income_by_month)
   

    average_transactions_list = []
    for i in iterations_per_month.values():
        
        average_transactions_list.append(i)
 
    balance_list = []
    balance = db.session.execute(db.select(Account.balance)).scalars()
    
    for bal in balance:
        balance_list.append(bal)
    
    balance_sum = sum(balance_list)
    
    cust_list = []
    cust_amount = db.session.execute(db.select(Customer)).scalars().all()
    customer_amount = len(cust_amount)
     
    
    today = date.today()
    yesterday = today - timedelta(days = 4)
    day_before_yesterday = yesterday - timedelta(days = 1)
    week_ago = today - timedelta(days = 7)
    
  
    latest_transactions = Transaction.query.order_by(Transaction.date.desc()).all()
 
 
    return render_template("index.html",
                           balance_sum=balance_sum,
                           customer_amount=customer_amount,
                           richest_customers_by_country=richest_customers_by_country,
                           total_customers_by_country=total_customers_by_country,
                           total_accounts_by_country=total_accounts_by_country,
                           transactions_by_country=transactions_by_country,
                           country_list_items=country_list_items,
                           selected_country=country,
                           balance_data_rich=balance_data_rich,
                           transaction_data_amount=transaction_data_amount,
                           transaction_data_operation=transaction_data_operation,
                           transaction_data_new_balance=transaction_data_new_balance,
                           labels=labels,
                           main_bar_color=main_bar_color,
                           maxrange=maxrange,
                           off_bar_color=off_bar_color,
                           iterations_per_week=iterations_per_week,
                           iterations_per_month=iterations_per_month,
                           average_transactions_list=average_transactions_list,
                           latest_transactions=latest_transactions,
                           now=datetime.now()
                           )



# Management routes

@main_bp.route("/management", methods=["GET", "POST"])
@login_required
def management():
    sort_order = request.args.get('sort_order', 'asc')
    sort_column = request.args.get('sort_by', 'id')
    search_word = request.args.get('q', '')
    
    page = request.args.get("page", 1, type=int)
    per_page = 50

    search_customers = get_filtered_customers(search_word)


    order_by = get_order_by_column(sort_column, sort_order)

    all_customers = search_customers.order_by(order_by).all()

    customers_pagination = search_customers.order_by(order_by).paginate(page=page, per_page=per_page, error_out=False)

    customer_pag = customers_pagination.items
    has_more = customers_pagination.has_next

    


    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify([
            {
                "id": cust.id,
                "name": f"{cust.given_name} {cust.surname}",
                "email": cust.email_address,
                "address": f"{cust.streetaddress}, {cust.zipcode}",
                "city": cust.city,
                "national_id": cust.national_id
            } for cust in customer_pag 
        ])


    customer_amount = search_customers.count()
    acc_amount = db.session.query(db.func.count(Account.id)).join(Customer, Customer.id == Account.customer_id).scalar()

    return render_template("management.html", customer_amount=customer_amount, acc_amount=acc_amount, all_customers=all_customers, q=search_word,customer_pag=customer_pag, has_more=has_more)




@main_bp.route("/management/customers", methods=["GET"])
def load_more_customers():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    sort_order = request.args.get('sort_order', 'asc')
    sort_column = request.args.get('sort_by', 'id')
    search_word = request.args.get('q', '')

    search_customers = get_filtered_customers(search_word)

    order_by = get_order_by_column(sort_column, sort_order)


    customers_pagination = search_customers.order_by(order_by).paginate(page=page, per_page=per_page, error_out=False)

    customers = [
        {
            "id": cust.id,
            "name": f"{cust.given_name} {cust.surname}",
            "email": cust.email_address,
            "address": f"{cust.streetaddress}, {cust.zipcode}",
            "city": cust.city,
            "national_id": cust.national_id
        }
        for cust in customers_pagination.items
    ]

    return jsonify({
        "customers": customers,
        "has_more": customers_pagination.has_next,
        "next_page": page + 1
    })



# Customer routes




@main_bp.route("/edit_customer", methods=["GET", "POST"])
@login_required
def edit_customer():
    customer_id = request.args.get("id")
    customer = db.get_or_404(Customer, customer_id)
    form = EditCustomerForm(obj=customer)
    
    if form.validate_on_submit():
        form.populate_obj(customer)
        db.session.commit()
        
        flash("Account successfully edited!")
        return redirect(url_for("main.management"))
    return render_template("edit_customer.html", form=form, customer=customer)



    

@main_bp.route("/customer/<int:id>", methods=["GET", "POST"])
@login_required
def customer_list(id):
    

    customer = Customer.query.get_or_404(id)
    selected_account_id = request.args.get("account_id", None, type=int)
    customer_accounts = customer.accounts  
    account_dict = {acc.id: acc for acc in customer_accounts} 
    

    if not selected_account_id and customer_accounts:
        selected_account_id = customer_accounts[0].id


    
    account_balances = {}

    customer_transaction_count = (
    Transaction.query
    .join(Account, Transaction.account_id == Account.id)
    .filter(Account.customer_id == customer.id)
    .with_entities(func.count(Transaction.id))
    .scalar()
    )

    customer_debit_count = (
        Transaction.query
        .join(Account, Transaction.account_id == Account.id)
        .filter(Account.customer_id == customer.id, Transaction.type == "DEBIT")
        .with_entities(func.count(Transaction.id))
        .scalar()
    )

    customer_credit_count = (
        Transaction.query
        .join(Account, Transaction.account_id == Account.id)
        .filter(Account.customer_id == customer.id, Transaction.type == "CREDIT")
        .with_entities(func.count(Transaction.id))
        .scalar()
    )


    customer_credit_sum = (
        Transaction.query
        .join(Account, Transaction.account_id == Account.id)
        .filter(Account.customer_id == customer.id, Transaction.type == "CREDIT")
        .with_entities(func.sum(Transaction.amount))
        .scalar()
    )
    
    customer_debit_sum = (
        Transaction.query
        .join(Account, Transaction.account_id == Account.id)
        .filter(Account.customer_id == customer.id, Transaction.type == "DEBIT")
        .with_entities(func.sum(Transaction.amount))
        .scalar()
    )
    
 
    account_balances = {account.id: account.balance for account in customer_accounts}
    total_balance = sum(account_balances.values())
    current_balance = account_balances.get(selected_account_id)
    page = request.args.get("page", 1, type=int)
    per_page = 20
    
    transactions_pagination = (
        Transaction.query
        .join(Account, Transaction.account_id == Account.id)
        .filter(Account.customer_id == customer.id, Transaction.account_id == selected_account_id)
        .order_by(Transaction.date.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    
    transactions = []
    
    if selected_account_id in account_dict:
        transactions = (
    Transaction.query
    .join(Account, Transaction.account_id == Account.id)
    .filter(Account.customer_id == customer.id, Transaction.account_id == selected_account_id)
    .order_by(Transaction.date.desc())
    .all()
)
    else:
        transactions = []
    
    transactions = transactions_pagination.items
    has_more = transactions_pagination.has_next
    
    cust_amount = db.session.execute(db.select(Customer)).scalars().all()
    customer_amount = len(cust_amount)
    
    
    return render_template(
        "customer.html",
        customer=customer,
        customer_accounts=customer_accounts,
        transactions=transactions,
        selected_account_id=selected_account_id,
        current_balance=current_balance,
        total_balance=total_balance, 
        zip=zip,
        total_accounts=len(customer_accounts),
        customer_debit_count=customer_debit_count,
        customer_credit_count=customer_credit_count,
        customer_credit_sum=customer_credit_sum,
        customer_debit_sum=customer_debit_sum,
        has_more=has_more,
        next_page=page+1,
        today = datetime.today().strftime("%d %b, %Y"),
        customer_amount=customer_amount
        
 
    )
    
    






  
@main_bp.route("/customer/<int:id>/transactions", methods=["GET"])
@login_required
def load_more_transactions(id):
    selected_account_id = request.args.get("account_id", None, type=int)
    page = request.args.get("page", 1, type=int)
    per_page = 20  

    transactions_pagination = (
        Transaction.query
        .join(Account, Transaction.account_id == Account.id)
        .filter(Account.customer_id == id, Transaction.account_id == selected_account_id)
        .order_by(Transaction.date.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    transactions = [
        {
            "id": t.id,
            "date": t.date.strftime('%d %b'),
            "type": t.type.value,
            "operation": t.operation.value,
            "amount": "{:,.2f}".format(t.amount),
        }
        for t in transactions_pagination.items
    ]

    return jsonify({
        "transactions": transactions,
        "has_more": transactions_pagination.has_next,
        "next_page": page + 1
    })




@main_bp.route("/add_customer", methods = ["GET", "POST"])
@roles_required("Admin")
def add_customer():
    
    form = AddCustomerForm()
    existing_customer = Customer.query.filter_by(national_id=form.national_id.data).first()
    if existing_customer:
            flash("A customer with this National ID already exists.", "danger")
            return redirect(url_for("main.add_customer"))
    if form.validate_on_submit():
        create_customer = Customer(
            given_name = form.given_name.data.title(),
            surname = form.surname.data.title(),
            streetaddress = form.streetaddress.data.title(),
            city = form.city.data.title(),
            zipcode = form.zipcode.data,
            country = form.country.data.title(),
            country_code = form.country_code.data.upper(),
            birthday = form.birthday.data,
            national_id = form.national_id.data,
            telephone_country_code = form.telephone_country_code.data,
            telephone = form.telephone.data,
            email_address = form.email_address.data.lower()
        )
        db.session.add(create_customer)
        db.session.commit()
        
        create_account = Account(
            account_type = form.account_type.data,
            created = datetime.now(),
            balance = form.balance.data,
            customer_id = create_customer.id
        )
        
        db.session.add(create_account)
        db.session.commit()
        
        create_transaction = Transaction(
            type = TransactionType.DEBIT,
            operation = TransactionOperation.DEPOSIT_CASH,
            date=datetime.now(),
            amount = form.balance.data,
            new_balance = form.balance.data,
            account_id = create_account.id
            
        )
        
        db.session.add(create_transaction)
        db.session.commit()
        flash("Account successfully created!", "success")
        return redirect(url_for("main.customer_list", id=create_customer.id))
    
    
    return render_template("add_customer.html", form=form)








@main_bp.route("/add_account/<int:customer_id>", methods=["GET", "POST"])
@login_required
def add_account(customer_id):
    form = AddAccountForm()
    customer = db.get_or_404(Customer, customer_id)

    if form.validate_on_submit():
        balance = form.balance.data


        if balance <= 0:
            flash("Balance must be greater than 0.", "danger")
            return render_template("add_account.html", form=form, customer=customer)

        if balance > 500000:
            flash("Balance cannot exceed 500,000.", "danger")
            return render_template("add_account.html", form=form, customer=customer)


        new_account = Account(
            account_type=form.account_type.data,
            created=datetime.now(),
            balance=balance,
            customer_id=customer.id
        )

        db.session.add(new_account)
        db.session.commit()


        initial_transaction = Transaction(
            type=TransactionType.DEBIT,
            operation=TransactionOperation.DEPOSIT_CASH,
            date=datetime.now(),
            amount=balance,
            new_balance=balance,
            account_id=new_account.id
        )

        db.session.add(initial_transaction)
        db.session.commit()

        flash("Account successfully created!", "success")
        return redirect(url_for("main.customer_list", id=customer_id))


    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.capitalize()}: {error}", "danger")

    return render_template("add_account.html", form=form, customer=customer)




@main_bp.route("/transfer", methods=["GET", "POST"])
@login_required
def transfer():
    currencies = ["USD", "EUR", "SEK", "GBP", "JPY"]
    
    
    
    latest_transactions =  Transaction.query.filter(Transaction.date <= datetime.now()).order_by(Transaction.date.desc()).all()
    country_data = get_country_data()
    
    transactions_by_country = country_data["transactions"]
    
    form = TransferForm()
    customers = Customer.query.all()
    accounts = Account.query.all()
    
    if form.validate_on_submit():
        sender_account_id = form.sender_account_id.data
        receiver_account_id = form.receiver_account_id.data
        amount = form.amount.data
        
        success, message = transfer_money(sender_account_id, receiver_account_id, amount)
        
        if success:
            flash("Transfer completed", "success")
            
        else:
            flash(message, "danger")
        
        return redirect(url_for("main.transfer"))
    
    
    
    return render_template("transfer.html", currencies=currencies, form=form, customers=customers, accounts=accounts, latest_transactions=latest_transactions, now=datetime.now(), today = datetime.today().strftime("%d %b"), transactions_by_country=transactions_by_country)






@main_bp.route("/unauthorized")
def unauthorized():
    return render_template("unauthorized.html")





# API ROUTES




@main_bp.route("/api/customer/<int:customer_id>", methods=["GET"])
@login_required
def api_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    customer_data = {
        "id": customer.id,
        "name": f"{customer.given_name} {customer.surname}",
        "email": customer.email_address,
        "accounts": [
            {"id": acc.id, "balance": float(acc.balance), "type": acc.account_type.value}
            for acc in customer.accounts
        ]
    }
    return jsonify(customer_data)






@main_bp.route("/api/accounts/<int:account_id>", methods=["GET"])
@login_required
def api_account(account_id):
    limit = request.args.get("limit", 20, type=int)
    offset = request.args.get("offset", 0, type=int)
    transactions = Transaction.query.filter_by(account_id=account_id)
    transactions = transactions.order_by(Transaction.date.desc()).offset(offset).limit(limit).all()
    transaction_list = [
        {
            "id": t.id,
            "date": t.date.strftime('%Y-%m-%d %H:%M:%S'),
            "type": t.type.value,
            "operation": t.operation.value,
            "amount": float(t.amount),
            "new_balance": float(t.new_balance)
        }
        for t in transactions
    ]
    return jsonify(transaction_list)


