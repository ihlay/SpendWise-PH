# SpendWise PH
 
A Filipino personal budgeting web app built with Django and SQLite.
 
## Features
- **Sweldo Tracker** - Track semi-monthly salary (1st & 15th), auto-detect next payday
- **Holiday Checker** - Nager.Date API integration for Philippine holidays
- **Utang Tracker** - Track debts (money owed and money lent)
- **Daily Spending Limit** - Auto-calculate how much you can spend per day
- **Savings Goals** - Set and track progress on savings goals
- **Needs vs Wants** - Tag transactions and see monthly breakdown
- **Analytics** - Most expensive day & category insights
- **PWA Support** - Installable as a mobile/desktop app
 
## Tech Stack
- Python 3.10+ / Django 4.2+
- SQLite
- Bootstrap 5
- Nager.Date Holiday API
- django-pwa
- django-allauth
 
## Setup Instructions
 
### 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/SpendWise-PH.git
cd SpendWise-PH
 
### 2. Create and activate virtual environment
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
 
### 3. Install dependencies
pip install -r requirements.txt — note: You MUST activate your Virtual Environment first
 
### 4. Run migrations
cd projectsite
python manage.py migrate
 
### 5. Create superuser
python manage.py createsuperuser
 
### 6. Load sample data (optional)
python manage.py create_initial_data
 
### 7. Run the server
python manage.py runserver
 
### 8. Open in browser
http://127.0.0.1:8000/
 
## API Used
- **Nager.Date Holiday API**: https://date.nager.at/api/v3/PublicHolidays/2026/PH
- No API key required
- Used to check if Philippine paydays fall on holidays
 
## Team Members
- **Eli** - Project Setup (GitHub, venv, Django config)
- **Fri** - Database & Models (models, admin, Faker data)
- **Amy** - UI & CRUD (forms, templates, views, URLs)
- **Ace** - Features & Auth (dashboard, login, PWA)
- **Miko** - API & Deployment (Sweldo, analytics, PythonAnywhere)
