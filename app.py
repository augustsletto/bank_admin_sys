from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from flask_migrate import Migrate, upgrade
from flask_bootstrap import Bootstrap5
from models import db, seedData, Customer, Account, Transaction, TransactionOperation, TransactionType
from collections import defaultdict
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
from datetime import datetime, timedelta, date
from collections import defaultdict
import requests
import os
from dotenv import load_dotenv
from wtforms import StringField, SubmitField, IntegerField, DateTimeField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, NumberRange, Length
from models import db, seedData, Customer, Account, Transaction, AccountType, TransactionType, TransactionOperation
from wtforms import StringField, DecimalField, SelectField, SubmitField
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, aliased
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text, func, cast
from sqlalchemy.sql import extract, func
from collections import Counter
from decimal import Decimal
load_dotenv()

POLYGON_API = os.getenv("POLYGON_API")
ALPHA_VANTAGE = os.getenv("ALPHA_VANTAGE")
CURRENCY_API = os.getenv("CURRENCY_API")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost:3310/Bank'
db.app = app
db.init_app(app)
migrate = Migrate(app,db)
Bootstrap5(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.jinja_env.filters['zip'] = zip




class EditCustomerForm(FlaskForm):
    given_name = StringField("Given Name", validators=[DataRequired(), Length(max=50)])
    surname = StringField("Surname", validators=[DataRequired(), Length(max=50)])
    streetaddress = StringField("Street Address", validators=[DataRequired(), Length(max=50)])
    city = StringField("City", validators=[DataRequired(), Length(max=70)])
    zipcode = StringField("Zip Code", validators=[DataRequired(), Length(max=15)])
    country = StringField("Country", validators=[DataRequired(), Length(max=60)])
    country_code = StringField("Country Code", validators=[DataRequired(), Length(max=2)])
    birthday = DateTimeField("Birthday (YYYY-MM-DD)", format='%Y-%m-%d', validators=[DataRequired()])
    national_id = StringField("National ID", validators=[DataRequired(), Length(max=20)])
    telephone_country_code = StringField("Telephone Country Code", validators=[DataRequired(), Length(max=10)])
    telephone = StringField("Telephone", validators=[DataRequired(), Length(max=30)])
    email_address = StringField("Email Address", validators=[DataRequired(), Email(), Length(max=50)])
    
    submit = SubmitField("Update Customer")


class AddCustomerForm(FlaskForm):
    given_name = StringField("Given Name", validators=[DataRequired(), Length(max=50)])
    surname = StringField("Surname", validators=[DataRequired(), Length(max=50)])
    streetaddress = StringField("Street Address", validators=[DataRequired(), Length(max=50)])
    city = StringField("City", validators=[DataRequired(), Length(max=70)])
    zipcode = StringField("Zip Code", validators=[DataRequired(), Length(max=15)])
    country = StringField("Country", validators=[DataRequired(), Length(max=60)])
    country_code = StringField("Country Code", validators=[DataRequired(), Length(max=2)])
    birthday = DateTimeField("Birthday (YYYY-MM-DD)", format='%Y-%m-%d', validators=[DataRequired()])
    national_id = StringField("National ID", validators=[DataRequired(), Length(max=20)])
    telephone_country_code = StringField("Telephone Country Code", validators=[DataRequired(), Length(max=10)])
    telephone = StringField("Telephone", validators=[DataRequired(), Length(max=30)])
    email_address = StringField("Email Address", validators=[DataRequired(), Email(), Length(max=50)])
    
    account_type = SelectField(
        "Account Type", 
        choices=[(account.value, account.name) for account in AccountType], 
        validators=[DataRequired()]
    )
    balance = DecimalField(
        "Initial Balance", 
        validators=[DataRequired(), NumberRange(min=0, message="Balance must be at least 0")], render_kw={"placeholder":"Balance"}
    )
    
    submit = SubmitField("Add Customer")


class AddAccountForm(FlaskForm):
    account_type = SelectField(
        "Account Type", 
        choices=[(account.value, account.name) for account in AccountType], 
        validators=[DataRequired()]
    )
    balance = DecimalField(
        "Initial Balance", 
        validators=[DataRequired(), NumberRange(min=0, message="Balance must be at least 0")]
    )
    submit = SubmitField("Create Account")

class TransferForm(FlaskForm):
    sender_account_id = SelectField("Sender Account", coerce=int, validators=[DataRequired()])
    receiver_account_id = SelectField("Receiver Account", coerce=int, validators=[DataRequired()])
    amount = DecimalField("Amount", validators=[DataRequired(), NumberRange(min=0.01, message="Amount must be positive")])
    submit = SubmitField("Transfer Money")

    def __init__(self, *args, **kwargs):
        super(TransferForm, self).__init__(*args, **kwargs)
        self.sender_account_id.choices = [(a.id, f"{a.customer.given_name} {a.customer.surname} - {a.account_type.value}") for a in Account.query.all()]
        self.receiver_account_id.choices = self.sender_account_id.choices




@app.route("/login", methods=["POST", "GET"])
def login():


    return render_template("login.html")




def get_country_data(country_name=None):
    
    AccountAlias = aliased(Account)
    

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







@app.route("/", methods=["GET"])
def startpage():
    
    
    
    country = request.args.get("country", "all")
    
    
    
    country_data = get_country_data(country)
    richest_customers_by_country = country_data["richest_customers"]
    
    total_customers_by_country = country_data["total_customers"]
    total_accounts_by_country = country_data["total_accounts"]
    transactions_by_country = country_data["transactions"]
    

    # print(richest_customers_by_country)
    
    
    
   
    
    
    
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
    iterations_income_by_month = dict(sorted(counter_income_by_month.items()))
   
    # print(iterations_income_by_month)
    
    
    
    average_transactions_list = []
    for i in iterations_per_month.values():
        
        average_transactions_list.append(i)
    #  / total_customers_by_country if total_customers_by_country else 1 
    

    
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
    
    

    currency_list = ["EUR", "CHF", "GBP", "JPY", "SEK"]
    currency_list_values = []
    
    
    for currency in currency_list:
        url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency={currency}&apikey={ALPHA_VANTAGE}'
        r = requests.get(url)
        data = r.json()['Realtime Currency Exchange Rate']['5. Exchange Rate']
        currency_list_values.append(data)

 
    

    url = f'https://www.alphavantage.co/query?function=REALTIME_BULK_QUOTES&symbol=BAC,WFC,GS,JPM&apikey={ALPHA_VANTAGE}'
    r = requests.get(url)
    data = r.json()["data"]
    
   
    bac = data[0]["close"]
    bac_pr = data[0]["previous_close"]
    bac_percent = data[0]["change_percent"]
    
    wfc = data[1]["close"]
    wfc_pr = data[1]["previous_close"]
    wfc_percent = data[1]["change_percent"]
    
    gs = data[2]["close"]
    gs_pr = data[2]["previous_close"]
    gs_percent = data[2]["change_percent"]
    
    jpm = data[3]["close"]
    jpm_pr = data[3]["previous_close"]
    jpm_percent = data[3]["change_percent"]

  
    
    return render_template("index.html", 
                           bac=bac, 
                           bac_pr=bac_pr,
                           bac_percent=bac_percent,
                           gs=gs,
                           gs_pr=gs_pr,
                           gs_percent=gs_percent,
                           jpm=jpm,
                           jpm_pr=jpm_pr,
                           jpm_percent=jpm_percent,
                           wfc=wfc,
                           wfc_pr=wfc_pr,
                           wfc_percent=wfc_percent,
                           currency_list_values=currency_list_values,
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
                           average_transactions_list=average_transactions_list
                           )






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

    
    



@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    currencies = ["USD", "EUR", "SEK", "GBP", "JPY"]
    
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
        
        return redirect(url_for("transfer"))
    
    
    
    return render_template("transfer.html", currencies=currencies, form=form, customers=customers, accounts=accounts)


@app.route("/add_account/<int:customer_id>", methods=["GET", "POST"])
def add_account(customer_id):
    
    form = AddAccountForm()
    customer = db.get_or_404(Customer, customer_id)
    
    
    if form.validate_on_submit():
        new_account = Account(
            account_type = form.account_type.data,
            created=datetime.now(),
            balance=form.balance.data,
            customer_id=customer.id
        )
        
        db.session.add(new_account)
        db.session.commit()
        
        initial_transaction = Transaction(
            type = TransactionType.DEBIT,
            operation = TransactionOperation.DEPOSIT_CASH,
            date=datetime.now(),
            amount = form.balance.data,
            new_balance = form.balance.data,
            account_id = new_account.id
            
        )
        
        db.session.add(initial_transaction)
        db.session.commit()
        flash("Account successfully created!", "success")
        return redirect(url_for("customer_list", id=customer_id))
    
    return render_template("add_account.html", form=form, customer=customer)



@app.route("/convert", methods=["GET"])
def convert_currency():
        try:
            amount = float(request.args.get('amount'))
            from_currency = request.args.get('from')
            to_currency = request.args.get('to')

            # Hämta växelkurser
            response = requests.get(f"https://v6.exchangerate-api.com/v6/{CURRENCY_API}/latest/{from_currency}")
            data = response.json()
            
            
            if to_currency not in data['conversion_rates']:
                return jsonify({"error": "Invalid currency code"}), 400

            exchange_rate = data['conversion_rates'][to_currency]
            converted_amount = round(amount * exchange_rate, 2)

            return jsonify({"converted_amount": converted_amount})

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    

    
@app.route("/management", methods=["GET", "POST"])
def management():
    # customer = db.session.execute(db.select(Customer)).scalars()
    
    
    customer = Customer.query
    
    
    
    sort_order = request.args.get("sort_order", "asc")
    sort_column = request.args.get("sort_column", "id")
    search_word = request.args.get('q', '')
    
    
    
    search_customers = Customer.query.filter(
        Customer.given_name.ilike("%"+ search_word + "%") |
        Customer.surname.ilike("%"+ search_word + "%") |
        Customer.streetaddress.ilike("%"+ search_word + "%") |
        Customer.country.ilike("%"+ search_word + "%") |
        Customer.city.ilike("%"+ search_word + "%") |
        Customer.id.ilike("%"+ search_word + "%") |
        Customer.national_id.ilike("%"+ search_word + "%")
)
    
    
    
    
    order_by = Customer.id
    if sort_column == "customers":
        order_by = Customer.given_name
    elif sort_column == "address":
        order_by = Customer.streetaddress
    elif sort_column == "city":
        order_by = Customer.city
    elif sort_column == "national_id":
        order_by = Customer.national_id
    elif sort_column == "id":
        order_by = Customer.id
    
    
    order_by = order_by.asc() if sort_order == "asc" else order_by.desc()
    
    all_customers = search_customers.order_by(order_by)
    
    
    
    
    cust_amount = db.session.execute(db.select(Customer)).scalars().all()
    customer_amount = len(cust_amount)
    acc_amount = db.session.query(db.func.count(Account.id)).join(Customer, Customer.id == Account.customer_id).scalar()
    
    
    
    
        
    
    return render_template("management.html", customer_amount=customer_amount, acc_amount=acc_amount, all_customers=all_customers, q=search_word)



@app.route("/download", )




@app.route("/test_customer")
def test_customer():
    return render_template("test_customer.html")

@app.route("/edit_customer", methods=["GET", "POST"])
def edit_customer():
    customer_id = request.args.get("id")
    customer = db.get_or_404(Customer, customer_id)
    form = EditCustomerForm(obj=customer)
    
    if form.validate_on_submit():
        form.populate_obj(customer)
        db.session.commit()
        
        flash("Account successfully edited!")
        return redirect(url_for("management"))
    return render_template("edit_customer.html", form=form, customer=customer)




@app.route("/customer/<int:id>", methods=["GET", "POST"])
def customer_list(id):
    customer = Customer.query.get_or_404(id)

    
   
    selected_account_id = request.args.get("account_id", None, type=int)
    
    customer_accounts = customer.accounts  
    account_dict = {acc.id: acc for acc in customer_accounts} 
    
    print(customer_accounts)
    
   
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
    
    
    print(customer_credit_sum)
    print(customer_debit_sum)
    
    
    account_balances = {account.id: account.balance for account in customer_accounts}
    
    
    total_balance = sum(account_balances.values())
    
    current_balance = account_balances.get(selected_account_id)
    
    page = request.args.get("page", 1, type=int)
    per_page = 10
    
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

        
        # .paginate(page=page, per_page=per_page, error_out=False)
        # transactions = pagination.items

   

    
    print(selected_account_id)
    
    
    
    transactions = transactions_pagination.items
    has_more = transactions_pagination.has_next
    
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
        has_more=has_more,
        next_page=page+1
        
        
        
        
        
    )
    
@app.route("/customer/<int:id>/transactions", methods=["GET"])
def load_more_transactions(id):
    selected_account_id = request.args.get("account_id", None, type=int)
    page = request.args.get("page", 1, type=int)
    per_page = 10  

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
            "date": t.date.strftime('%b %d, %Y'),
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

    
    
@app.route("/add_customer", methods = ["GET", "POST"])
def add_customer():
    
    form = AddCustomerForm()
        
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
        return redirect(url_for("customer_list", id=create_customer.id))
    
    
    return render_template("add_customer.html", form=form)










if __name__  == "__main__":
    with app.app_context():
        upgrade()
        seedData(db)
    app.run(debug=True)