import logging
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
from workforce.services.helper_service import generate_beneficiary_id
from decimal import Decimal, InvalidOperation
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db import transaction


logger = logging.getLogger(__name__)


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


    def update_confirmation(self, user, data):
        # instance = WorkforceEisBankAdvice.objects.get(id= extract_uuid(data["id"]))
        instance = WorkforceEisBankAdvice.objects.get(id= data["id"])
        instance.is_confirmed = True
        instance.remarks= "The Bank Advice was Confirmed"
        instance.save(username=user.username)
        return "success"

    def revert_confirmation(self, user, data):
        # instance = WorkforceEisBankAdvice.objects.get(id= extract_uuid(data["id"]))
        instance = WorkforceEisBankAdvice.objects.get(id= data["id"])
        instance.is_confirmed = False
        instance.remarks= "The Bank Advice was Reverted"
        instance.save(username=user.username)
        return "success"
