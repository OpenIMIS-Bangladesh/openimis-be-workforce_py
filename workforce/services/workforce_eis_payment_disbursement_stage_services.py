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
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from datetime import date
from django.db import transaction
import calendar
from calendar import monthrange


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
        year = int(year)
        month = int(month)

        for eis_process_id in eis_process_ids:
            process_id= extract_uuid(eis_process_id)
            workforce_eis_payment_process= WorkforceEisPaymentProcess.objects.get(id=process_id)
            workforce_application= workforce_eis_payment_process.workforce_application

            calculation_start_date = None
            day_inclusive_calculation= True
            exists_in_stage = WorkforceEisPaymentDisbursementStage.objects.filter(beneficiary_id=workforce_eis_payment_process.beneficiary_id, is_deleted=False).first()
            #FIRST DISBURSEMENT ARREAR CALCULATION NUMBER OF MONTHS ================
            if exists_in_stage is None:
                day_inclusive_calculation= True
                if workforce_application.application_type == "disabilityAssistance":
                    doctor_json = json.loads(
                        workforce_application.doctors_entry) if workforce_application.doctors_entry else None
                    if doctor_json is None:
                        return False
                    accident_info_json = json.loads(
                        workforce_application.employee_accident_info) if workforce_application.employee_accident_info else None


                    calculation_start_date = accident_info_json.get("dateOfRejoining") if accident_info_json.get(
                        "dateOfRejoining") else doctor_json.get("dateOfAssessment")
                    calculation_start_date = datetime.strptime(calculation_start_date, "%Y-%m-%d").date() if isinstance(
                        calculation_start_date, str) else calculation_start_date
                else:
                    accident_info_json = json.loads(
                        workforce_application.employee_accident_info) if workforce_application.employee_accident_info else None
                    if accident_info_json is None:
                        return False
                    calculation_start_date = accident_info_json.get("dateOfDeath") if accident_info_json.get(
                        "dateOfDeath") else None
                    calculation_start_date = datetime.strptime(calculation_start_date, "%Y-%m-%d").date() if isinstance(
                        calculation_start_date, str) else calculation_start_date
            #if beneficiary were on hold, then take the hold date as calculation start date...
            elif workforce_eis_payment_process.beneficiary_status =="hold":
                day_inclusive_calculation= True
                calculation_start_date = workforce_eis_payment_process.last_live_check_date
            #search if payment is clear for previous month
            else:
                day_inclusive_calculation= False
                if month-1==0:
                    prev_month=12
                    search_year= year-1
                else:
                    prev_month= month-1
                    search_year= year
                prev_month_payment= WorkforceEisPaymentDisbursementStage.objects.filter(beneficiary_id= workforce_eis_payment_process.beneficiary_id, year=search_year, month_index= prev_month, is_deleted=False).first()
                if prev_month_payment is None:
                    last_payment= WorkforceEisPaymentDisbursementStage.objects.filter(beneficiary_id= workforce_eis_payment_process.beneficiary_id, is_deleted=False).order_by('-year', '-month_index').first()
                    if last_payment is not None:
                        last_pay_year= last_payment.year
                        last_pay_month= last_payment.month_index
                        if last_pay_month == 12:
                            next_month = 1
                            set_year = last_pay_year + 1
                        else:
                            next_month = last_pay_month + 1
                            set_year = last_pay_year
                        calculation_start_date = date(set_year, next_month, 1)

            last_day = monthrange(year, month)[1]
            target_date = date(year, month, last_day)
            if calculation_start_date is not None:
                if day_inclusive_calculation:

                    rd = relativedelta(target_date, calculation_start_date)

                    months = rd.years * 12 + rd.months
                    fraction = rd.days / monthrange(target_date.year, target_date.month)[1]

                    months_gone = months + fraction
                    # months_gone= round(months_gone, 1)
                else:
                    months_gone = (target_date.year - calculation_start_date.year) * 12 + (target_date.month - calculation_start_date.month) + 1
                pay_from_date = calculation_start_date
                pay_to_date = target_date
            else:
                months_gone = 1

            if workforce_eis_payment_process.eis_payment_type!="monthly":
                if workforce_eis_payment_process.eis_payment_type=="installment":
                    installment_count=WorkforceEisPaymentDisbursementStage.objects.filter(is_deleted=False, beneficiary_id= workforce_eis_payment_process.beneficiary_id).count()
                    installment_count+=1
                months_gone = 1
            else:
                installment_count=None

            if months_gone==1:
                pay_from_date = date(year, month, 1)
                pay_to_date = target_date


            if safe_decimal(workforce_eis_payment_process.arrear_payment_month) == safe_decimal(month) -1 and safe_decimal(workforce_eis_payment_process.arrear_payment_year) == safe_decimal(year):
                paid_amount = safe_decimal(workforce_eis_payment_process.payable_amount) + safe_decimal(workforce_eis_payment_process.arrear_amount)
            else:
                payable_amount = safe_decimal(workforce_eis_payment_process.payable_amount).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )

                months_gone = safe_decimal(months_gone).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )

                paid_amount = (payable_amount * months_gone).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            new_stage= WorkforceEisPaymentDisbursementStage(
                workforce_eis_payment_process= workforce_eis_payment_process,
                workforce_application = workforce_eis_payment_process.workforce_application,
                workforce_application_summary = workforce_eis_payment_process.workforce_application_summary,
                workforce_employee_dependent = workforce_eis_payment_process.workforce_employee_dependent,
                bank = workforce_eis_payment_process.bank,
                bank_account_no = workforce_eis_payment_process.bank_account_no,
                routing_number = workforce_eis_payment_process.routing_number,
                bank_account_holder_name = workforce_eis_payment_process.bank_account_holder_name,
                eis_payment_type = workforce_eis_payment_process.eis_payment_type,
                eis_calculated_amount = workforce_eis_payment_process.eis_calculated_amount,
                eis_approved_amount = workforce_eis_payment_process.eis_approved_amount,
                eis_initial_replacement_rate = workforce_eis_payment_process.eis_initial_replacement_rate,
                eis_initial_monthly_amount = workforce_eis_payment_process.eis_initial_monthly_amount,
                eis_monthly_amount = workforce_eis_payment_process.eis_monthly_amount,
                paid_amount= paid_amount,
                # paid_amount= workforce_eis_payment_process.paid_amount,
                increment_amount = workforce_eis_payment_process.increment_amount,
                decrement_amount = workforce_eis_payment_process.decrement_amount,
                total_adjustment_amount = workforce_eis_payment_process.total_adjustment_amount,
                month_index = month,
                year = year,
                processing_date = date.today(),
                is_disbursed = False,
                is_confirmed = False,
                approved = "yes",
                beneficiary_id = workforce_eis_payment_process.beneficiary_id,
                phone_number = workforce_eis_payment_process.phone_number,
                pay_from_date= pay_from_date,
                pay_to_date= pay_to_date,
                serial_number = workforce_eis_payment_process.serial_number,
                installment_number= installment_count or None
            )
            try:
                new_stage.save(username=user.username)
                if workforce_eis_payment_process.beneficiary_status=="hold":
                    try:
                        workforce_eis_payment_process.status= "inactive"
                        workforce_eis_payment_process.save(username=user.username)
                    except Exception as e:
                        continue
                    new_main_row= WorkforceEisPaymentProcess(
                        workforce_application=workforce_eis_payment_process.workforce_application,
                        workforce_application_summary=workforce_eis_payment_process.workforce_application_summary,
                        workforce_employee_dependent=workforce_eis_payment_process.workforce_employee_dependent,
                        bank=workforce_eis_payment_process.bank,
                        bank_account_no=workforce_eis_payment_process.bank_account_no,
                        routing_number=workforce_eis_payment_process.routing_number,
                        bank_account_holder_name=workforce_eis_payment_process.bank_account_holder_name,
                        eis_payment_type=workforce_eis_payment_process.eis_payment_type,
                        payment_type_remarks=workforce_eis_payment_process.payment_type_remarks,
                        eis_calculated_amount=workforce_eis_payment_process.eis_calculated_amount,
                        eis_approved_amount=workforce_eis_payment_process.eis_approved_amount,
                        eis_initial_replacement_rate=workforce_eis_payment_process.eis_initial_replacement_rate,
                        eis_initial_monthly_amount=workforce_eis_payment_process.eis_initial_monthly_amount,
                        eis_monthly_amount=workforce_eis_payment_process.eis_monthly_amount,
                        increment_amount=workforce_eis_payment_process.increment_amount,
                        increment_date=workforce_eis_payment_process.increment_date,
                        decrement_amount=workforce_eis_payment_process.decrement_amount,
                        decrement_date=workforce_eis_payment_process.decrement_date,
                        month_index=workforce_eis_payment_process.month_index,
                        year=workforce_eis_payment_process.year,
                        processing_date=workforce_eis_payment_process.processing_date,
                        is_disbursed=workforce_eis_payment_process.is_disbursed,
                        approved=workforce_eis_payment_process.approved,
                        beneficiary_id=workforce_eis_payment_process.beneficiary_id,
                        beneficiary_status="eligible",
                        status="active",
                        reason=workforce_eis_payment_process.reason,
                        remarks=None,
                        remarriage_or_death_date=None,
                        last_live_check_date=None,
                        live_check_remarks=None,
                        payable_amount=workforce_eis_payment_process.payable_amount,
                        phone_number=workforce_eis_payment_process.phone_number,
                        serial_number=workforce_eis_payment_process.serial_number
                    )

                    try:
                        new_main_row.save(username=user.username)
                    except Exception as e:
                        return e
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