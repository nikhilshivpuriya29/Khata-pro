from datetime import date, datetime
from config import Config


def calc_months_elapsed(from_date, to_date=None):
    """Calculate months elapsed between two dates (fractional)."""
    if to_date is None:
        to_date = date.today()
    if isinstance(from_date, datetime):
        from_date = from_date.date()
    if isinstance(to_date, datetime):
        to_date = to_date.date()
    delta = to_date - from_date
    return max(delta.days / 30.0, 0)


def calc_interest(principal, from_date, to_date=None):
    """Simple interest: P × R × T (2% per month)."""
    months = calc_months_elapsed(from_date, to_date)
    return round(principal * Config.INTEREST_RATE * months, 2)


def get_customer_balance(customer):
    """Calculate total principal outstanding, interest, and total due."""
    total_credit = 0.0
    total_debit = 0.0
    total_interest = 0.0

    for txn in customer.transactions:
        if txn.txn_type == "credit":
            total_credit += txn.amount
            total_interest += calc_interest(txn.amount, txn.purchase_date)
        else:
            total_debit += txn.amount

    principal_due = total_credit - total_debit
    # Interest only on outstanding principal (not negative)
    if principal_due <= 0:
        total_interest = 0.0

    return {
        "total_credit": round(total_credit, 2),
        "total_debit": round(total_debit, 2),
        "principal_due": round(max(principal_due, 0), 2),
        "interest": round(total_interest, 2),
        "total_due": round(max(principal_due, 0) + total_interest, 2),
    }


def get_ledger_with_balance(transactions):
    """Return transactions with running balance and interest info."""
    ledger = []
    running = 0.0
    for txn in sorted(transactions, key=lambda t: (t.purchase_date, t.created_at)):
        if txn.txn_type == "credit":
            running += txn.amount
            interest = calc_interest(txn.amount, txn.purchase_date)
        else:
            running -= txn.amount
            interest = 0.0

        is_overdue = False
        if txn.promised_date and txn.txn_type == "credit":
            is_overdue = date.today() > txn.promised_date and running > 0

        ledger.append({
            "txn": txn,
            "running_balance": round(running, 2),
            "interest": round(interest, 2),
            "is_overdue": is_overdue,
        })
    return ledger
