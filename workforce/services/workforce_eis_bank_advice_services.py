import logging
import calendar
from core.services import BaseService
from pamqp.decode import double
from workforce.models import WorkforceEmployeeDependent, WorkforceApplication, WorkforceEmployee, WorkforceFactory, \
    WorkforceEisPaymentProcess, Bank, WorkforceEisPaymentDisbursement, WorkforceEisPaymentDisbursementStage, \
    WorkforceEisBankAdvice
from datetime import datetime, timezone, date
import requests
import json
import os
import base64
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from math import floor
from workforce.services.helper_service import generate_beneficiary_id, build_payment_confirmation_link, shorten_url
from decimal import Decimal, InvalidOperation
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db import transaction

from workforce.services.workforce_sms_services import send_sms

logger = logging.getLogger(__name__)


def get_bangla_month(month_index):
    months = [
        "জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল",
        "মে", "জুন", "জুলাই", "আগস্ট",
        "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর"
    ]

    if 1 <= month_index <= 12:
        return months[month_index - 1]
    return "অবৈধ মাস"

def get_english_month(month_index):
    months = [
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December"
    ]

    if 1 <= month_index <= 12:
        return months[month_index - 1]
    return "Invalid Month"

def to_bangla_numbers(text: str) -> str:
    bangla_digits = {
        '0': '০',
        '1': '১',
        '2': '২',
        '3': '৩',
        '4': '৪',
        '5': '৫',
        '6': '৬',
        '7': '৭',
        '8': '৮',
        '9': '৯'
    }

    return ''.join(bangla_digits.get(char, char) for char in text)

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def safe_decimal(value, default=Decimal("0.0")):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return default

def calculate_age_in_months(effective_date):
    if not effective_date:
        return None

    if isinstance(effective_date, str):
        try:
            eff_date = datetime.strptime(effective_date, "%Y-%m-%d %H:%M:%S.%f %z")
        except ValueError:
            try:
                eff_date = datetime.strptime(effective_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                eff_date = datetime.strptime(effective_date, "%Y-%m-%d")
    elif isinstance(effective_date, date):
        eff_date = datetime.combine(effective_date, datetime.min.time())
    else:
        eff_date = effective_date

    now = datetime.now(timezone.utc)

    months = (now.year - eff_date.year) * 12 + (now.month - eff_date.month)

    if now.day < eff_date.day:
        months -= 1

    return months


def parse_frontend_date(date_str):
    """Parses Y-m-d string to date object. Returns None if empty/invalid."""
    if not date_str or date_str == "":
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def calculate_months_difference(start_date, end_date):
    """Calculates the number of months between two dates."""
    if not start_date or not end_date:
        return 0
    diff = relativedelta(end_date, start_date)
    return diff.years * 12 + diff.months

def extract_uuid(encoded_str):
    decoded = base64.b64decode(encoded_str).decode()
    return decoded.split(":")[1]


class WorkforceEisBankAdviceServices(BaseService):
    OBJECT_TYPE = WorkforceEisBankAdvice

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)

    @transaction.atomic
    def create_bank_advice(self, user, data):
        stage_ids = data.get("payment_disbursement_stage_ids", [])
        today = date.today()

        # WorkforceEisBankAdvice.objects.filter(
        #     month=data["month"],
        #     year=data["year"]
        # ).delete()

        bank_advice = WorkforceEisBankAdvice(
            advice_date=today,
            is_confirmed=False,
            confirmation_date=today,
            month=data["month"],
            year=data["year"]
        )

        try:
            bank_advice.save(username=user.username)

            for encoded_stage_id in stage_ids:
                stage_id = extract_uuid(encoded_stage_id)

                stage_instance = WorkforceEisPaymentDisbursementStage.objects.filter(id=stage_id).first()
                if not stage_instance:
                    continue

                stage_instance.workforce_eis_bank_advice = bank_advice
                stage_instance.save(username=user.username)

        except Exception as e:
            logger.error(f"Bank advice creation failed: {e}")
            raise

        return "success"



    @transaction.atomic
    def update_confirmation(self, user, data):

        today = date.today()

        instance = WorkforceEisBankAdvice.objects.get(id=data["id"])

        stage_instances = WorkforceEisPaymentDisbursementStage.objects.filter(
            workforce_eis_bank_advice_id=data["id"]
        )

        for stage_instance in stage_instances:
            WorkforceEisPaymentDisbursement.objects.filter(
                beneficiary_id=stage_instance.beneficiary_id,
                month_index=stage_instance.month_index,
                year=stage_instance.year
            ).delete()

            disburse_instance = WorkforceEisPaymentDisbursement(
                workforce_eis_payment_disbursement_stage=stage_instance,
                workforce_application=stage_instance.workforce_application,
                workforce_application_summary=stage_instance.workforce_application_summary,
                workforce_employee_dependent=stage_instance.workforce_employee_dependent,
                bank=stage_instance.bank,
                bank_account_no=stage_instance.bank_account_no,
                bank_account_holder_name=stage_instance.bank_account_holder_name,
                eis_payment_type=stage_instance.eis_payment_type,
                eis_calculated_amount=stage_instance.eis_calculated_amount,
                eis_approved_amount=stage_instance.eis_approved_amount,
                eis_initial_replacement_rate=stage_instance.eis_initial_replacement_rate,
                eis_initial_monthly_amount=stage_instance.eis_initial_monthly_amount,
                eis_monthly_amount=stage_instance.eis_monthly_amount,
                paid_amount=stage_instance.paid_amount,
                month_index=stage_instance.month_index,
                year=stage_instance.year,
                disbursement_date=today,
                beneficiary_id=stage_instance.beneficiary_id,
                phone_number=stage_instance.phone_number
            )
            try:
                disburse_instance.save(username=user.username)
                stage_instance.is_disbursed = True
                stage_instance.disbursement_date = today
                try:
                    stage_instance.save(username=user.username)
                    # full_month_name_in_bangla= get_bangla_month(stage_instance.month_index)
                    full_month_name_in_english= get_english_month(stage_instance.month_index)
                    # year_in_bangla= to_bangla_numbers(str(stage_instance.year))
                    year_in_english= str(stage_instance.year)
                    phone_number= stage_instance.phone_number
                    confirmation_url= build_payment_confirmation_link(stage_instance.id)
                    confirmation_url_shortened= shorten_url(confirmation_url)
                    message = f"""Dear beneficiary, Please confirm your payment of {full_month_name_in_english}, {year_in_english} From EIS-PILOT With the following link. Please Contact: 01886921030 For any query.
                    {confirmation_url_shortened}
                    """
                    # message = f"""সম্মানিত বেনিফিট গ্রহীতা,
                    # ই.আই.এস পাইলট হতে আপনার প্রাপ্য {full_month_name_in_bangla}, {year_in_bangla} মাসের মাসিক টপ-আপ বেনিফিট আপনার ব্যাংক অ্যাকাউন্টে প্রেরিত হয়েছে। অনুগ্রহ পূর্বক নিম্নউল্লেখিত মোবাইল নাম্বারে SMS এর মাধ্যমে অথবা নিম্নউল্লেখিত লিংকে ভিজিট করে টাকা প্রাপ্তি নিশ্চিত করুন।
                    # প্রয়োজনে যোগাযোগ
                    # মোবাইল: ০১৮৮৬৯২১০৩০
                    # প্রাপ্তি নিশ্চিতের জন্য লিংকঃ {confirmation_url}
                    # ই-মেইল: specialunit@eis-pilot-bd.org
                    # ঠিকানা: ১৯৬, ১০ম তলা, ই.আই.এস পাইলট স্পেশাল ইউনিট, শ্রম ভবন, শহীদ সৈয়দ নজরুল ইসলাম সরণি, বিজয়নগর, ঢাকা-১০০০
                    # """
                    send_sms(phone_number, message)
                except Exception as e:
                    continue
            except Exception as e:
                continue
        instance.is_confirmed = True
        instance.remarks = "The Bank Advice was Confirmed"
        try:
            instance.save(username=user.username)
        except Exception as e:
            raise e
        return "success"

    def revert_confirmation(self, user, data):
        # instance = WorkforceEisBankAdvice.objects.get(id= extract_uuid(data["id"]))
        instance = WorkforceEisBankAdvice.objects.get(id= data["id"])
        instance.is_confirmed = False
        instance.remarks= "The Bank Advice was Reverted"
        instance.save(username=user.username)
        return "success"
