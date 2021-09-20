from celery import task
from micro_admin.models import SavingsAccount
from decimal import Decimal as d
from datetime import datetime
import calendar


@task()
def calculate_interest_of_savings_account():
    savings_accounts = SavingsAccount.objects.filter(status='Approved')
    for savings_account in savings_accounts:
        current_date = datetime.now().date()
        year_days = 366 if calendar.isleap(current_date.year) else 365
        daily_interest_rate_charged = (
            savings_account.savings_balance * savings_account.annual_interest_rate) / (d(year_days) * 100)
        savings_account.savings_balance += daily_interest_rate_charged
        savings_account.save()

# c094 2021-08-03T10:03:51 fix(business): startup settings

# c101 2021-08-19T11:20:40 tighten bootstrap config

# c108 2021-09-04T11:37:29 verify: deployment entrypoint

# c115 2021-09-20T11:54:18 wire the initial project files
