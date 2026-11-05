from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dateutil.utils import today
from django.utils import timezone
from datetime import date, datetime

from pydantic.types import Decimal

from workforce.models import WorkforceEisPaymentProcess

scheduler = BackgroundScheduler()
_started = False

import os
import logging
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.models import Q

from workforce.models import WorkforceEisPaymentProcess, WorkforceDocument
from workforce.services.workforce_sms_services import send_sms

logger = logging.getLogger(__name__)


def send_nine_month_biometric_verification_link():
    """
    Scheduled job (runs daily):
    Finds active payment records on 'hold' whose last live check date
    (or initial processing date) is >= 9 months old, and sends them
    a biometric verification link via SMS.
    """
    today = date.today()
    nine_months_ago = today - relativedelta(months=9)
    logger.info(f"[Scheduler] Checking 'hold' beneficiaries due for verification before: {nine_months_ago}")

    PHOTO_TYPES = {
        "nominee's photo",
        "nominee photo",
        "employee photo",
        "workers photo",
        "photo of worker",
    }

    # 1. Query payments on 'hold' where last_live_check_date is >= 9 months ago
    hold_payments = WorkforceEisPaymentProcess.objects.filter(
        status="active",
        beneficiary_status="hold",
    ).filter(
        Q(last_live_check_date__lte=nine_months_ago) |
        Q(last_live_check_date__isnull=True, processing_date__lte=nine_months_ago)
    )

    logger.info(f"[Scheduler] Found {hold_payments.count()} 'hold' records due for 9-month live check.")

    for payment in hold_payments:
        try:
            # 2. Prevent duplicate SMS spamming if already sent today
            # if payment.live_check_remarks and f"sent via SMS on {today}" in payment.live_check_remarks:
            #     logger.debug(f"[Scheduler] SMS already sent today for payment {payment.id}. Skipping.")
            #     continue

            # 3. Resolve Beneficiary Name (Dependent vs. Employee vs. Account Holder)
            dependent = payment.workforce_employee_dependent
            employee = getattr(payment.workforce_application, "workforce_employee", None)

            if dependent:
                beneficiary_name = dependent.name_bn or dependent.name_en or payment.bank_account_holder_name
            elif employee:
                beneficiary_name = employee.first_name_bn or employee.first_name_en or payment.bank_account_holder_name
            else:
                beneficiary_name = payment.bank_account_holder_name or "Beneficiary"

            # 4. Resolve Phone Number
            phone_number = (
                payment.phone_number
                or (dependent.phone_number if dependent else None)
                or (employee.phone_number if employee else None)
            )

            if not phone_number:
                logger.warning(f"[Scheduler] No phone number for payment ID {payment.id} ({beneficiary_name}). Skipping.")
                continue

            # 5. Fetch Reference Photo Document ID
            doc_query = WorkforceDocument.objects.filter(
                workforce_application_id=payment.workforce_application.id,
                document_type__in=PHOTO_TYPES,
                is_deleted=False,
            )

            if dependent:
                photo_doc = doc_query.filter(workforce_dependent=dependent).first() or doc_query.first()
            else:
                photo_doc = doc_query.first()

            if not photo_doc:
                logger.error(f"[Scheduler] No photo document for application {payment.workforce_application_id}. Cannot create link.")
                continue

            document_id = str(photo_doc.uuid if hasattr(photo_doc, "uuid") and photo_doc.uuid else photo_doc.id)

            # 6. Compose Link & SMS Message
            frontend_base_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
            verify_url = f"{frontend_base_url}/front/biometric/verify/{document_id}"
            message = f"Hi, {beneficiary_name} , Please verify your identity at {verify_url}"

            # 7. Dispatch SMS
            sms_response = send_sms(sms_to=phone_number, message=message)
            logger.info(f"[Scheduler] SMS sent to {phone_number} (Payment ID {payment.id}). Response: {sms_response}")

            # 8. Update WorkforceEisPaymentProcess audit & live check tracking columns
            payment.live_check_remarks = f"Verification link sent via SMS on {today} to {phone_number}"
            payment.remarks = f"Awaiting 9-month live check (SMS link sent: {today})"
            payment.save(username="Scheduler")

        except Exception as e:
            logger.error(f"[Scheduler] Error processing payment ID {payment.id}: {e}")
            continue

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
            payable_amount=payment.payable_amount + payment.decrement_amount,
            serial_number=payment.serial_number
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
    # NEW: Run once every 24 hours to check who has reached the 9-month threshold
    scheduler.add_job(
        send_nine_month_biometric_verification_link,
        # trigger=IntervalTrigger(hours=24),  # or CronTrigger(hour=9, minute=0) for 9:00 AM daily
        trigger=IntervalTrigger(seconds=30),  # Run every 30 seconds for testing
        next_run_time=datetime.now(),
        id="nine_month_biometric_verification_job",
        replace_existing=True,
    )

    scheduler.start()
    _started = True
