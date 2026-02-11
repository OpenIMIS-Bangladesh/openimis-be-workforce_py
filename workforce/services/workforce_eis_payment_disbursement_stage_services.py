import logging
from core.services import BaseService
from pamqp.decode import double
from workforce.models import WorkforceEmployeeDependent, WorkforceApplication, WorkforceEmployee, WorkforceFactory, \
    WorkforceEisPaymentProcess, Bank, WorkforceEisPaymentDisbursementStage
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


class WorkforceEisPaymentDisbursementStageServices(BaseService):
    OBJECT_TYPE = WorkforceEisPaymentDisbursementStage

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)

    def create_payment_stage(self, user, data):
        eis_process_ids= data["workforceEisPaymentProcessIdIn"]
        month= data["month"]
        year= data["year"]

        for eis_process_id in eis_process_ids:
            process_id= extract_uuid(eis_process_id)
            workforce_eis_payment_process= WorkforceEisPaymentProcess.objects.get(id=process_id)
            new_stage= WorkforceEisPaymentDisbursementStage(
                workforce_eis_payment_process= workforce_eis_payment_process,
                workforce_application = workforce_eis_payment_process.workforce_application,
                workforce_application_summary = workforce_eis_payment_process.workforce_application_summary,
                workforce_employee_dependent = workforce_eis_payment_process.workforce_employee_dependent,
                bank = workforce_eis_payment_process.bank,
                bank_account_no = workforce_eis_payment_process.bank_account_no,
                bank_account_holder_name = workforce_eis_payment_process.bank_account_holder_name,
                eis_payment_type = workforce_eis_payment_process.eis_payment_type,
                eis_calculated_amount = workforce_eis_payment_process.eis_calculated_amount,
                eis_approved_amount = workforce_eis_payment_process.eis_approved_amount,
                eis_initial_replacement_rate = workforce_eis_payment_process.eis_initial_replacement_rate,
                eis_initial_monthly_amount = workforce_eis_payment_process.eis_initial_monthly_amount,
                eis_monthly_amount = workforce_eis_payment_process.eis_monthly_amount,
                paid_amount= workforce_eis_payment_process.payable_amount,
                increment_amount = workforce_eis_payment_process.increment_amount,
                decrement_amount = workforce_eis_payment_process.decrement_amount,
                total_adjustment_amount = workforce_eis_payment_process.total_adjustment_amount,
                month_index = month,
                year = year,
                processing_date = date.today(),
                is_disbursed = False,
                is_confirmed = False,
                approved = "yes",
                beneficiary_id = workforce_eis_payment_process.beneficiary_id
            )
            try:
                new_stage.save(username=user.username)
            except Exception as e:
                continue
        return "success"


    def delete_payment_stage(self, user, data):
        eis_stage_ids= data["workforceEisPaymentStageIdIn"]

        for eis_stage_id in eis_stage_ids:
            stage_id= extract_uuid(eis_stage_id)
            workforce_eis_payment_stage= WorkforceEisPaymentDisbursementStage.objects.get(id=stage_id)

            try:
                workforce_eis_payment_stage.delete(username= user.username)
            except Exception as e:
                continue
        return "success"