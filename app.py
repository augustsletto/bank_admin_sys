from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_migrate import Migrate, upgrade
from flask_bootstrap import Bootstrap5
from models import db, seedData, Customer, Account, Transaction
from collections import defaultdict
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import requests


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost:3310/Bank'
db.app = app
db.init_app(app)
migrate = Migrate(app,db)


# STOCK_API = ""

@app.route("/", methods=["GET"])
def startpage():
    
#     stock_params = {
#     "function": "BATCH_STOCK_QUOTES",
#     "symbols": "AAPL,MSFT,GOOGL,TSLA,AMZN",
#     "apikey": STOCK_API,
# }

#     response = requests.get("https://www.alphavantage.co/query", params=stock_params)

    

    url = "https://api.marketdata.app/v1/stocks/bulkquotes/?symbols=AAPL,META,MSFT"
    response = requests.request("GET", url)
								 															
    print(response.json())

    

    
    # print(data)
    
    
    # response = requests.get("https://api.currencyapi.com/v3/latest?apikey=cur_live_kS4B4miMHw2gDQeJiU4sEJ03vNdVWVvSKd9OsnLX")
    
    # result = response.json()
    # print(result)
    
    return render_template("index.html")




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

    # Default to the first available account
    if not selected_account_id and customer_accounts:
        selected_account_id = customer_accounts[0].id

    # Get the latest balance for each account
    account_balances = {}
    for account in customer_accounts:
        last_transaction = (
            Transaction.query.filter(Transaction.account_id == account.id)
            .order_by(Transaction.date.desc())
            .first()
        )
        account_balances[account.id] = last_transaction.new_balance if last_transaction else 0.00

    # Compute total balance across all accounts
    total_balance = sum(account_balances.values())

    # Get paginated transactions for the selected account
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