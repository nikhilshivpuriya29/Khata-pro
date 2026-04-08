# Khata Pro — Credit-Debit Management System

A web-based Credit-Debit (Udhar/Khata) management system built for Indian shop owners and small businesses.

## Features

- **Multi-user Auth** — Each shop owner gets isolated data with login/register
- **Customer KYC** — Full name, father's name, phone, Aadhaar (masked), complete address with Indian states
- **Credit & Payment Tracking** — Record udhar (credit given) and payments received with item descriptions
- **Promised Date & Overdue Alerts** — Track repayment promises, highlight overdue entries
- **2% Monthly Interest** — Auto-calculated simple interest on outstanding principal
- **Dashboard** — Total outstanding, interest accrued, overdue count, top debtors, recent transactions
- **Reports** — Outstanding report, overdue report, date-filtered transaction report
- **CSV Export** — Export outstanding and transaction reports
- **AI-Ready** — Customer `risk_score` field for future credit-scoring model
- **Local + Cloud** — SQLite for local use, PostgreSQL-ready for cloud deployment

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000

## Cloud Mode

```bash
export KHATA_MODE=cloud
export DATABASE_URL=postgresql://user:pass@host:5432/khata
python app.py
```

## Tech Stack

- Python, Flask, SQLAlchemy, Flask-Login
- Bootstrap 5, Bootstrap Icons
- SQLite (local) / PostgreSQL (cloud)
