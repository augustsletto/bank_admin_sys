from wtforms import StringField, SubmitField, DateTimeField, DecimalField, SelectField, RadioField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, NumberRange, Length
from app.models import Account, AccountType


class EditCustomerForm(FlaskForm):
    given_name = StringField("Given Name", validators=[DataRequired(), Length(min=2, max=50)])
    surname = StringField("Surname", validators=[DataRequired(), Length(min=2, max=50)])
    streetaddress = StringField("Street Address", validators=[DataRequired(), Length(min=2, max=50)])
    city = StringField("City", validators=[DataRequired(), Length(min=2, max=70)])
    zipcode = StringField("Zip Code", validators=[DataRequired(), Length(min=2, max=15)])
    country = StringField("Country", validators=[DataRequired(), Length(min=2, max=60)])
    country_code = StringField("Country Code", validators=[DataRequired(), Length(min=2, max=2)])
    birthday = DateTimeField("Birthday (YYYY-MM-DD)", format='%Y-%m-%d', validators=[DataRequired()])
    national_id = StringField("National ID", validators=[DataRequired(), Length(min=2, max=20)])
    telephone_country_code = StringField("Telephone Country Code", validators=[DataRequired(), Length(min=1, max=10)])
    telephone = StringField("Telephone", validators=[DataRequired(), Length(min=5, max=30)])
    email_address = StringField("Email Address", validators=[DataRequired(), Email(), Length(min=5, max=50)])
    
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
    balance = DecimalField("Initial Balance", validators=[DataRequired(), NumberRange(min=1, max=500000, message="Balance must be between 0 and 500,000")], render_kw={"placeholder":"Balance"}
    )
    
    submit = SubmitField("Add Customer")


class AddAccountForm(FlaskForm):
    account_type = SelectField(
        "Account Type", 
        choices=[(account.value, account.name) for account in AccountType], 
        validators=[DataRequired()]
    )
    balance = DecimalField("Initial Balance", validators=[DataRequired(), NumberRange(min=1, max=500000, message="Balance must be between 1 and 500,000")])
    submit = SubmitField("Create Account")

class TransferForm(FlaskForm):
    sender_account_id = RadioField("Sender Account", coerce=int, validators=[DataRequired()])
    receiver_account_id = RadioField("Receiver Account", coerce=int, validators=[DataRequired()])
    amount = DecimalField("Amount", validators=[DataRequired(), NumberRange(min=1, max=500000, message="Amount must be positive")])
    submit = SubmitField("Transfer Money")

    def __init__(self, *args, **kwargs):
        super(TransferForm, self).__init__(*args, **kwargs)
        self.sender_account_id.choices = [
            (a.id, f"{a.customer.given_name} {a.customer.surname} | {a.account_type.value} | ${a.balance:,.2f}")
            for a in Account.query.all()
        ]
        self.receiver_account_id.choices = self.sender_account_id.choices



