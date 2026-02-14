from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dateutil.utils import today
from django.utils import timezone
from datetime import date, datetime

from pydantic.types import Decimal

from workforce.models import WorkforceEisPaymentProcess

scheduler = BackgroundScheduler()
_started = False


def my_test_job():
    today= date.today()
    print(today)
    # Filter rows where decrement_end_date equals today and decrement_amount > 0
    decremented_payments = WorkforceEisPaymentProcess.objects.filter(
        decrement_end_date__lte=today,
        decrement_amount__gt=0,
        status="active"
    )

    # Loop through filtered rows
    for payment in decremented_payments:
        print(payment.id, payment.payable_amount, payment.decrement_amount)
        new_row= WorkforceEisPaymentProcess(
            workforce_application=payment.workforce_application,
            workforce_application_summary=payment.workforce_application_summary,
            workforce_employee_dependent=payment.workforce_employee_dependent,
            bank=payment.bank,
            bank_account_no=payment.bank_account_no,
            bank_account_holder_name=payment.bank_account_holder_name,
            eis_payment_type=payment.eis_payment_type,
            eis_calculated_amount=payment.eis_calculated_amount,
            eis_approved_amount=payment.eis_approved_amount,
            eis_initial_replacement_rate=payment.eis_initial_replacement_rate,
            eis_initial_monthly_amount=payment.eis_initial_monthly_amount,
            eis_monthly_amount=payment.eis_monthly_amount,
            month_index=payment.month_index,
            year=payment.year,
            processing_date=today,
            is_disbursed=payment.is_disbursed,
            approved=payment.approved,
            beneficiary_id=payment.beneficiary_id,
            beneficiary_status=payment.beneficiary_status,
            status="active",
            reason= None,
            remarks="Automatically updated payable amount as decrementing period ended",
            payable_amount=payment.payable_amount + payment.decrement_amount
        )
        new_row.save(username="Admin")

        payment.status = "inactive"
        payment.save(username="Admin")


def start():
    global _started

    if _started:
        return

    scheduler.add_job(
        my_test_job,
        trigger=IntervalTrigger(hours=10),
        id="test_print_job",
        replace_existing=True,
    )

    scheduler.start()
    _started = True
