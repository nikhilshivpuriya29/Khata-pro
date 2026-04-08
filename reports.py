import csv
import io
from flask import Blueprint, render_template, request, Response
from flask_login import login_required, current_user
from datetime import datetime, date
from models import Customer, Transaction
from interest import get_customer_balance

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports")
@login_required
def reports_page():
    return render_template("reports.html")


@reports_bp.route("/reports/outstanding")
@login_required
def outstanding_report():
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    data = []
    for c in customers:
        bal = get_customer_balance(c)
        if bal["principal_due"] > 0:
            data.append({"customer": c, "balance": bal})
    data.sort(key=lambda x: x["balance"]["total_due"], reverse=True)
    return render_template("report_outstanding.html", data=data)


@reports_bp.route("/reports/overdue")
@login_required
def overdue_report():
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    overdue = []
    for c in customers:
        for txn in c.transactions:
            if txn.txn_type == "credit" and txn.promised_date and txn.promised_date < date.today():
                bal = get_customer_balance(c)
                overdue.append({"customer": c, "txn": txn, "balance": bal})
    overdue.sort(key=lambda x: x["txn"].promised_date)
    return render_template("report_overdue.html", overdue=overdue, today=date.today())


@reports_bp.route("/reports/transactions")
@login_required
def transaction_report():
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    query = Transaction.query.join(Customer).filter(Customer.user_id == current_user.id)
    if from_date:
        query = query.filter(Transaction.purchase_date >= datetime.strptime(from_date, "%Y-%m-%d").date())
    if to_date:
        query = query.filter(Transaction.purchase_date <= datetime.strptime(to_date, "%Y-%m-%d").date())
    txns = query.order_by(Transaction.purchase_date.desc()).all()
    return render_template("report_transactions.html", txns=txns, from_date=from_date or "", to_date=to_date or "")


@reports_bp.route("/reports/export/outstanding")
@login_required
def export_outstanding():
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Customer", "Phone", "Principal Due", "Interest", "Total Due"])
    for c in customers:
        bal = get_customer_balance(c)
        if bal["principal_due"] > 0:
            writer.writerow([c.full_name, c.phone, bal["principal_due"], bal["interest"], bal["total_due"]])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=outstanding_{date.today()}.csv"},
    )


@reports_bp.route("/reports/export/transactions")
@login_required
def export_transactions():
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    query = Transaction.query.join(Customer).filter(Customer.user_id == current_user.id)
    if from_date:
        query = query.filter(Transaction.purchase_date >= datetime.strptime(from_date, "%Y-%m-%d").date())
    if to_date:
        query = query.filter(Transaction.purchase_date <= datetime.strptime(to_date, "%Y-%m-%d").date())
    txns = query.order_by(Transaction.purchase_date.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Customer", "Type", "Amount", "Item", "Promised Date", "Note"])
    for t in txns:
        writer.writerow([
            t.purchase_date, t.customer.full_name, t.txn_type.upper(),
            t.amount, t.item_description, t.promised_date or "", t.note,
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=transactions_{date.today()}.csv"},
    )
