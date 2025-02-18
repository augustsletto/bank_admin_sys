from flask import Flask, render_template, request, redirect, url_for, jsonify
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
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, NumberRange
from models import db, seedData, Customer, Account, Transaction
from wtforms import StringField, DecimalField, SelectField, SubmitField
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

load_dotenv()

POLYGON_API = os.getenv("POLYGON_API")
ALPHA_VANTAGE = os.getenv("ALPHA_VANTAGE")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost:3310/Bank'
db.app = app
db.init_app(app)
migrate = Migrate(app,db)


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')




@app.route("/", methods=["GET"])
def startpage():
    

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

        print(data)
    

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
                           currency_list_values=currency_list_values
                           )


@app.route("/management", methods=["GET"])
def management():
    customer = db.session.execute(db.select(Customer)
                                  .order_by(Customer.surname)).scalars()
    print(customer)
    
    
    return render_template("management.html", customer=customer)

@app.route("/customer/<int:id>", methods=["GET"])
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
        "customers.html",
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