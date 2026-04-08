from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import date, datetime
from models import db, Customer, Transaction
from interest import get_customer_balance, get_ledger_with_balance

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def dashboard():
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    total_customers = len(customers)
    total_principal = 0.0
    total_interest = 0.0
    total_due = 0.0
    overdue_count = 0
    top_debtors = []

    for c in customers:
        bal = get_customer_balance(c)
        total_principal += bal["principal_due"]
        total_interest += bal["interest"]
        total_due += bal["total_due"]
        top_debtors.append({"customer": c, "balance": bal})
        # Check overdue
        for txn in c.transactions:
            if txn.txn_type == "credit" and txn.promised_date and txn.promised_date < date.today():
                overdue_count += 1
                break

    top_debtors.sort(key=lambda x: x["balance"]["total_due"], reverse=True)
    recent_txns = (
        Transaction.query.join(Customer)
        .filter(Customer.user_id == current_user.id)
        .order_by(Transaction.created_at.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "dashboard.html",
        total_customers=total_customers,
        total_principal=round(total_principal, 2),
        total_interest=round(total_interest, 2),
        total_due=round(total_due, 2),
        overdue_count=overdue_count,
        top_debtors=top_debtors[:5],
        recent_txns=recent_txns,
    )


# ── Customer CRUD ──────────────────────────────────────────────

@main_bp.route("/customers")
@login_required
def customers():
    q = request.args.get("q", "").strip()
    query = Customer.query.filter_by(user_id=current_user.id)
    if q:
        query = query.filter(
            db.or_(
                Customer.full_name.ilike(f"%{q}%"),
                Customer.phone.ilike(f"%{q}%"),
                Customer.aadhaar.ilike(f"%{q}%"),
            )
        )
    custs = query.order_by(Customer.full_name).all()
    balances = {c.id: get_customer_balance(c) for c in custs}
    return render_template("customers.html", customers=custs, balances=balances, q=q)


@main_bp.route("/customer/add", methods=["GET", "POST"])
@login_required
def add_customer():
    if request.method == "POST":
        c = Customer(
            user_id=current_user.id,
            full_name=request.form["full_name"].strip(),
            father_name=request.form.get("father_name", "").strip(),
            phone=request.form.get("phone", "").strip(),
            aadhaar=request.form.get("aadhaar", "").strip(),
            address_street=request.form.get("address_street", "").strip(),
            address_city=request.form.get("address_city", "").strip(),
            address_district=request.form.get("address_district", "").strip(),
            address_state=request.form.get("address_state", "").strip(),
            address_pin=request.form.get("address_pin", "").strip(),
        )
        db.session.add(c)
        db.session.commit()
        flash(f"Customer '{c.full_name}' added.", "success")
        return redirect(url_for("main.customers"))
    return render_template("customer_form.html", customer=None)


@main_bp.route("/customer/<int:cid>/edit", methods=["GET", "POST"])
@login_required
def edit_customer(cid):
    c = Customer.query.filter_by(id=cid, user_id=current_user.id).first_or_404()
    if request.method == "POST":
        c.full_name = request.form["full_name"].strip()
        c.father_name = request.form.get("father_name", "").strip()
        c.phone = request.form.get("phone", "").strip()
        c.aadhaar = request.form.get("aadhaar", "").strip()
        c.address_street = request.form.get("address_street", "").strip()
        c.address_city = request.form.get("address_city", "").strip()
        c.address_district = request.form.get("address_district", "").strip()
        c.address_state = request.form.get("address_state", "").strip()
        c.address_pin = request.form.get("address_pin", "").strip()
        db.session.commit()
        flash("Customer updated.", "success")
        return redirect(url_for("main.customer_detail", cid=c.id))
    return render_template("customer_form.html", customer=c)


@main_bp.route("/customer/<int:cid>/delete", methods=["POST"])
@login_required
def delete_customer(cid):
    c = Customer.query.filter_by(id=cid, user_id=current_user.id).first_or_404()
    db.session.delete(c)
    db.session.commit()
    flash(f"Customer '{c.full_name}' deleted.", "warning")
    return redirect(url_for("main.customers"))


@main_bp.route("/customer/<int:cid>")
@login_required
def customer_detail(cid):
    c = Customer.query.filter_by(id=cid, user_id=current_user.id).first_or_404()
    balance = get_customer_balance(c)
    ledger = get_ledger_with_balance(c.transactions)
    return render_template("customer_detail.html", customer=c, balance=balance, ledger=ledger)


# ── Transactions ───────────────────────────────────────────────

@main_bp.route("/customer/<int:cid>/credit", methods=["GET", "POST"])
@login_required
def add_credit(cid):
    c = Customer.query.filter_by(id=cid, user_id=current_user.id).first_or_404()
    if request.method == "POST":
        txn = Transaction(
            customer_id=c.id,
            txn_type="credit",
            amount=float(request.form["amount"]),
            item_description=request.form.get("item_description", "").strip(),
            purchase_date=datetime.strptime(request.form["purchase_date"], "%Y-%m-%d").date(),
            promised_date=datetime.strptime(request.form["promised_date"], "%Y-%m-%d").date() if request.form.get("promised_date") else None,
            note=request.form.get("note", "").strip(),
        )
        db.session.add(txn)
        db.session.commit()
        flash(f"Credit of ₹{txn.amount:,.2f} recorded for {c.full_name}.", "success")
        return redirect(url_for("main.customer_detail", cid=c.id))
    return render_template("transaction_form.html", customer=c, txn_type="credit", txn=None)


@main_bp.route("/customer/<int:cid>/payment", methods=["GET", "POST"])
@login_required
def add_payment(cid):
    c = Customer.query.filter_by(id=cid, user_id=current_user.id).first_or_404()
    if request.method == "POST":
        txn = Transaction(
            customer_id=c.id,
            txn_type="debit",
            amount=float(request.form["amount"]),
            purchase_date=datetime.strptime(request.form["purchase_date"], "%Y-%m-%d").date(),
            note=request.form.get("note", "").strip(),
        )
        db.session.add(txn)
        db.session.commit()
        flash(f"Payment of ₹{txn.amount:,.2f} received from {c.full_name}.", "success")
        return redirect(url_for("main.customer_detail", cid=c.id))
    return render_template("transaction_form.html", customer=c, txn_type="debit", txn=None)


@main_bp.route("/transaction/<int:tid>/delete", methods=["POST"])
@login_required
def delete_transaction(tid):
    txn = Transaction.query.get_or_404(tid)
    c = Customer.query.filter_by(id=txn.customer_id, user_id=current_user.id).first_or_404()
    db.session.delete(txn)
    db.session.commit()
    flash("Transaction deleted.", "warning")
    return redirect(url_for("main.customer_detail", cid=c.id))
