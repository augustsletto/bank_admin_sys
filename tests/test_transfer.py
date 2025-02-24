import pytest
from app import app, db, transfer_money
from models import Customer, Account, Transaction, TransactionType, TransactionOperation
from datetime import datetime
from decimal import Decimal

@pytest.fixture
def test_client():
    """Setup Flask test client and database."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  
    client = app.test_client()

    with app.app_context():
        db.create_all()
        yield client
        # db.drop_all()

def create_test_accounts():
    """Helper function to create test customers and accounts."""
    customer = Customer(
        given_name="John",
        surname="Doe",
        streetaddress="123 Test St",
        city="Testville",
        zipcode="12345",
        country="Testland",
        country_code="TL",
        birthday=datetime(1990, 1, 1),
        national_id="123456789",
        telephone_country_code="+1",
        telephone="555-1234",
        email_address="john.doe@example.com"
    )
    db.session.add(customer)
    db.session.commit()

    account1 = Account(
        account_type="Checking",
        created=datetime.now(),
        balance=Decimal("500.00"),  
        customer_id=customer.id
    )

    account2 = Account(
        account_type="Savings",
        created=datetime.now(),
        balance=Decimal("1000.00"),  
        customer_id=customer.id
    )

    db.session.add_all([account1, account2])
    db.session.commit()

    return account1, account2

def test_cannot_transfer_more_than_balance(test_client):
    """Test that transferring more money than the sender has is blocked."""
    with app.app_context():
        account1, account2 = create_test_accounts()

        success, message = transfer_money(account1.id, account2.id, Decimal("600.00"))  
        assert not success
        assert message == "Insufficient balance."

def test_cannot_transfer_negative_amount(test_client):
    """Test that negative transfers are blocked."""
    with app.app_context():
        account1, account2 = create_test_accounts()

        success, message = transfer_money(account1.id, account2.id, Decimal("-50.00"))  
        assert not success
        assert message == "Invalid amount: Cannot transfer negative money."
