import pytest
from app import create_app, db
from app.models import Account, Customer, Transaction, TransactionType, TransactionOperation
from app.utils import transfer_money
from datetime import datetime
from decimal import Decimal

@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_db(app):
    with app.app_context():
        customer = Customer(
            given_name="Mr",
            surname="Cool",
            streetaddress="123 Huvudgata",
            city="Silicon Valley",
            zipcode="1337",
            country="Örnsköldsvik",
            country_code="XD",
            birthday=datetime(1990, 1, 1),
            national_id="123456789",
            telephone_country_code="+1",
            telephone="1234567890",
            email_address="Mrcool@yahootmail.com"
        )
        db.session.add(customer)
        db.session.commit()

        account1 = Account(
            account_type="SAVINGS",
            created=datetime.now(),
            balance=Decimal("1000.00"),
            customer_id=customer.id
        )

        account2 = Account(
            account_type="CHECKING",
            created=datetime.now(),
            balance=Decimal("500.00"),
            customer_id=customer.id
        )

        db.session.add(account1)
        db.session.add(account2)
        db.session.commit()

       
        db.session.refresh(account1)
        db.session.refresh(account2)

        return customer, account1, account2



def test_transfer_exceed_balance(init_db):
    _, sender, receiver = init_db
    success, message = transfer_money(sender.id, receiver.id, Decimal("2000.00"))
    assert success is False
    assert message == "Insufficient balance."

def test_transfer_negative_amount(init_db):
    _, sender, receiver = init_db
    success, message = transfer_money(sender.id, receiver.id, Decimal("-50.00"))
    assert success is False
    assert message == "Cannot transfer negative money."

def test_transfer_valid_amount(init_db, app):
    _, sender, receiver = init_db

    with app.app_context():
        success, message = transfer_money(sender.id, receiver.id, Decimal("200.00"))

        assert success is True
        assert message == "Successful!"


        sender = db.session.get(Account, sender.id)
        receiver = db.session.get(Account, receiver.id)

        assert sender.balance == Decimal("800.00")
        assert receiver.balance == Decimal("700.00")

    """
    A QA engineer walks into a bar and orders a beer.
He orders 2 beers.
He orders 0 beers.
He orders -1 beers.
He orders a lizard.
He orders a 304jfo"#)=¤().
He tries to leave without paying.
Satisfied, he declares the bar ready for business. The first customer comes in an orders a beer. 
They finish their drink, and then ask where the bathroom is.
The bar explodes.
    """