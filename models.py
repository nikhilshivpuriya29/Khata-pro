from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    shop_name = db.Column(db.String(150), nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customers = db.relationship("Customer", backref="owner", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Customer(db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    father_name = db.Column(db.String(120))
    phone = db.Column(db.String(15))
    aadhaar = db.Column(db.String(12))
    address_street = db.Column(db.String(200))
    address_city = db.Column(db.String(100))
    address_district = db.Column(db.String(100))
    address_state = db.Column(db.String(100))
    address_pin = db.Column(db.String(6))
    risk_score = db.Column(db.Float, default=0.0)  # For future AI model
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship("Transaction", backref="customer", lazy=True, cascade="all, delete-orphan")

    @property
    def masked_aadhaar(self):
        if self.aadhaar and len(self.aadhaar) >= 4:
            return "XXXX-XXXX-" + self.aadhaar[-4:]
        return "N/A"

    @property
    def full_address(self):
        parts = [self.address_street, self.address_city, self.address_district, self.address_state]
        addr = ", ".join(p for p in parts if p)
        if self.address_pin:
            addr += f" - {self.address_pin}"
        return addr or "N/A"


class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    txn_type = db.Column(db.String(10), nullable=False)  # "credit" or "debit"
    amount = db.Column(db.Float, nullable=False)
    item_description = db.Column(db.String(300))
    purchase_date = db.Column(db.Date, nullable=False, default=date.today)
    promised_date = db.Column(db.Date)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
