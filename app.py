from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_migrate import Migrate, upgrade
from flask_bootstrap import Bootstrap5
from models import db, seedData, Customer, Account, Transaction
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
from models import db, seedData, Customer, Account, Transaction, AccountType
from wtforms import StringField, DecimalField, SelectField, SubmitField
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, aliased
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text


load_dotenv()

POLYGON_API = os.getenv("POLYGON_API")
ALPHA_VANTAGE = os.getenv("ALPHA_VANTAGE")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost:3310/Bank'
db.app = app
db.init_app(app)
migrate = Migrate(app,db)
Bootstrap5(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


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





@app.route("/login")
def login():

    
    

    return render_template("login.html")


# def get_customer_and_accounts_from_country(country_name):
#     customers_with_accounts = (
#         db.session.query(Customer, Account
#                         ).join(Account, Customer.id == Account.customer_id
#                         ).filter(Customer.country == country_name
#                         ).all()
#     )
    
#     return customers_with_accounts

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
    
    
    
    
    # customer_accounts = (
    #     db.session.query(Customer, db.func.sum(Account.balance).label("total_balance")
    #                     ).join(Account, Customer.id == Account.customer_id
    #                     ).filter(Customer.country == country_name
    #                     ).group_by(Customer.id
    #                     ).order_by(db.desc("total_balance")
    #                     ).limit(limit
    #                     ).all()
    # )
    
    # total_customers = db.session.query(db.func.count(Customer.id)
    #                                 ).filter(Customer.country == country_name
    #                                 ).scalar()

    # total_accounts = (
    #     db.session.query(db.func.count(Account.id)
    #                     ).join(Customer, Customer.id == Account.customer_id
    #                     ).filter(Customer.country == country_name
    #                     ).scalar()
    # )

    # # Count total transactions in the country
    # # total_transactions = (
    # #     db.session.query(db.func.count(Transaction.id))
    # #     .join(Account, Account.id == Transaction.account_id)
    # #     .join(Customer, Customer.id == Account.customer_id)
    # #     .filter(Customer.country == country_name)
    # #     .scalar()
    # # )
    # transactions = (
    #     db.session.query(Transaction
    #                     ).join(Account, Account.id == Transaction.account_id
    #                     ).join(Customer, Customer.id == Account.customer_id
    #                     ).filter(Customer.country == country_name
    #                     ).order_by(Transaction.date.desc()
    #                     ).all()
    # )



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
            "transactions": transaction_list
            
            }







@app.route("/", methods=["GET"])
def startpage():
    
    country = request.args.get("country", "all")
    
    
    
    country_data = get_country_data(country)
    richest_customers_by_country = country_data["richest_customers"]
    total_customers_by_country = country_data["total_customers"]
    total_accounts_by_country = country_data["total_accounts"]
    transactions_by_country = country_data["transactions"]
    
    
    
    country_list_items = db.session.execute(db.select(Customer.country)).scalars().all()
    
    
    
    
    balance_list = []
    balance = db.session.execute(db.select(Account.balance)).scalars()
    
    for bal in balance:
        balance_list.append(bal)
    
    balance_sum = sum(balance_list)
    
    cust_list = []
    cust_amount = db.session.execute(db.select(Customer)).scalars().all()
    customer_amount = len(cust_amount)
    
    
    # customers_account = get_customer_and_accounts_from_country(country_name)
    
    
    # top_richest_list = []
    # customer_dict = {}
    # for customer, account in customers_account[:10]:
    #     print(f"Customer: {customer.given_name} {customer} {customer.country}")
    #     print(f"acc id{account.id}")
    
    
    
    # custumers_country = Customer.query.filter_by(Customer.country.desc()).all()
    
    
    
    
    
    today = date.today()
    yesterday = today - timedelta(days = 4)
    day_before_yesterday = yesterday - timedelta(days = 1)
    week_ago = today - timedelta(days = 7)
    
    
    # TODO: Currency trader
    currency_list = ["EUR", "CHF", "GBP", "JPY", "SEK"]
    currency_list_values = []
    
    
    for currency in currency_list:
        url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency={currency}&apikey={ALPHA_VANTAGE}'
        r = requests.get(url)
        data = r.json()['Realtime Currency Exchange Rate']['5. Exchange Rate']
        currency_list_values.append(data)

        # print(data)
    

    url = f'https://www.alphavantage.co/query?function=REALTIME_BULK_QUOTES&symbol=BAC,WFC,GS,JPM&apikey={ALPHA_VANTAGE}'
    r = requests.get(url)
    data = r.json()["data"]
    
    # print(data)
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
                           selected_country=country
                           )


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
        flash("Account successfully created!", "success")
        return redirect(url_for("management"))
    
    return render_template("add_account.html", form=form, customer=customer)

# @app.route("/delete_account/<int:account_id>" methods=["GET", "POST"])
# def delete_account(account_id):
#     pass

@app.route("/convert", methods=["GET"])
def convert_currency():
        try:
            amount = float(request.args.get('amount'))
            from_currency = request.args.get('from')
            to_currency = request.args.get('to')

            # Hämta växelkurser
            response = requests.get(f"https://v6.exchangerate-api.com/v6/793f97b4f7bfbf99ae6fb376/latest/{from_currency}")
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
    customer = db.session.execute(db.select(Customer)).scalars()
    # print(customer)
    
    # currency_list = ["EUR", "CHF", "GBP", "JPY", "SEK"]
    # currency_list_values = []
    currencies = ["USD", "EUR", "SEK", "GBP", "JPY"]
    
    # for currency in currency_list:
    #     url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency={currency}&apikey={ALPHA_VANTAGE}'
    #     r = requests.get(url)
    #     data = r.json()['Realtime Currency Exchange Rate']['5. Exchange Rate']
    #     currency_list_values.append(data)
        
    # url = f"https://v6.exchangerate-api.com/v6/793f97b4f7bfbf99ae6fb376/latest/USD"
    # data = requests.get(url).json()
        
    # print(data)
    
        
        
    
    return render_template("management.html", customer=customer, currencies=currencies)

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

    # Get selected account ID and page number from request 
    selected_account_id = request.args.get("account_id", None, type=int)
    page = request.args.get("page", 1, type=int)
    per_page = 5

    # Fetch all accounts for this customer
    customer_accounts = customer.accounts  # List of all accounts
    account_dict = {acc.id: acc for acc in customer_accounts}  # Map accounts by ID

    # Default to the first available acc
    if not selected_account_id and customer_accounts:
        selected_account_id = customer_accounts[0].id

    # Get the latest balance for each acc
    account_balances = {}
    for account in customer_accounts:
        last_transaction = (
            Transaction.query.filter(Transaction.account_id == account.id)
            .order_by(Transaction.date.desc())
            .first()
        )
        account_balances[account.id] = last_transaction.new_balance if last_transaction else 0.00

    # Compute total balance
    total_balance = sum(account_balances.values())

    # Get paginated for account
    transactions = []
    pagination = None
    current_balance = account_balances.get(selected_account_id, 0.00)

    if selected_account_id in account_dict:
        pagination = (
            Transaction.query.filter(Transaction.account_id == selected_account_id)
            .order_by(Transaction.date.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
        transactions = pagination.items

    return render_template(
        "customer.html",
        customer=customer,
        customer_accounts=customer_accounts,
        transactions=transactions,
        pagination=pagination,
        selected_account_id=selected_account_id,
        current_balance=current_balance,
        total_balance=total_balance, 
        page=page
    )



if __name__  == "__main__":
    with app.app_context():
        upgrade()
        seedData(db)
    app.run(debug=True)