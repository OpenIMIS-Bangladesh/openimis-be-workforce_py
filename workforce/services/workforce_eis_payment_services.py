import logging

from OpenSSL.rand import status
from core.models import user
from core.services import BaseService
from pamqp.decode import double
from workforce.models import WorkforceEmployeeDependent, WorkforceApplication, WorkforceEmployee, WorkforceFactory, \
    WorkforceEisPaymentProcess, Bank
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
from dateutil.relativedelta import relativedelta
from django.db import transaction


logger = logging.getLogger(__name__)


def extract_uuid(encoded_str):
    decoded = base64.b64decode(encoded_str).decode()
    return decoded.split(":")[1]

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


THREE_DECIMAL = Decimal("0.001")

def round_three(value):
    return value.quantize(THREE_DECIMAL, rounding=ROUND_HALF_UP)


class WorkforceEisPaymentServices(BaseService):
    OBJECT_TYPE = WorkforceEisPaymentProcess

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)

    def create_payment_schedule(user, workforce_application_id):
        workforce_application = WorkforceApplication.objects.get(id= workforce_application_id)
        association = workforce_application.association_type
        accident_type = workforce_application.application_type
        # interactive_user = InteractiveUser.objects.get(id=user.id) if user else None
        if workforce_application.application_type == "disabilityAssistance":
            bank_info = json.loads(workforce_application.employee_bank_info)
            bank_id = (
                base64.b64decode(bank_info[0]["branch"]["id"])
                .decode("utf-8")
                .split(":")[1]
            )
            bank_instance = Bank.objects.get(id=bank_id)

            approved_amount = safe_decimal(workforce_application.eis_approved_amount) if workforce_application.eis_approved_amount is not None else 0
            now = datetime.now()
            beneficiary_id = generate_beneficiary_id(
                association, accident_type, workforce_application.id
            )

            # ---------- SAVE FULL MONTH PAYMENTS ----------
            if WorkforceEisPaymentProcess.objects.filter(workforce_application=workforce_application).exists():
                return False
            if approved_amount>0:
                payment_obj = WorkforceEisPaymentProcess(
                    workforce_application=workforce_application,
                    bank=bank_instance,
                    bank_account_no=bank_info[0]["accountNumber"],
                    bank_account_holder_name=bank_info[0]["accountHolderName"],
                    eis_payment_type="monthly",
                    eis_calculated_amount=workforce_application.eis_calculated_amount,
                    eis_approved_amount=workforce_application.eis_approved_amount,
                    eis_initial_replacement_rate=workforce_application.initial_replacement_rate,
                    eis_initial_monthly_amount=workforce_application.eis_initial_monthly_amount,
                    eis_monthly_amount=workforce_application.eis_monthly_amount,
                    month_index=now.month,
                    year=now.year,
                    processing_date=date.today(),
                    beneficiary_id=beneficiary_id,
                    is_disbursed=False,
                    payable_amount=workforce_application.eis_monthly_amount,
                    phone_number= workforce_application.workforce_employee.phone_number or None
                )
                payment_obj.save(username=user.username)
            return None
        else:
            accident_info_json = json.loads(workforce_application.employee_accident_info) if workforce_application.employee_accident_info else None
            if accident_info_json is None:
                return False
            dependents=WorkforceEmployeeDependent.objects.filter(workforce_application= workforce_application)
            dependent_count=0
            beneficiary_id_of_employee=""
            for dep in dependents:
                if dep.bank_id is None:
                    continue
                if WorkforceEisPaymentProcess.objects.filter(workforce_employee_dependent= dep).exists():
                    continue
                if dep.is_eligible and dep.eis_approved_amount is not None and dep.eis_approved_amount > 0:
                    bank_instance= Bank.objects.get(id= dep.bank_id)
                    now = datetime.now()
                    dependent_count = dependent_count+1
                    beneficiary_id = generate_beneficiary_id(association, accident_type, workforce_application.id, str(dependent_count))

                    payment_obj = WorkforceEisPaymentProcess(
                        workforce_application=workforce_application,
                        bank=bank_instance,
                        bank_account_no=dep.bank_account_no,
                        bank_account_holder_name=dep.bank_account_holder_name,
                        eis_payment_type="monthly",
                        eis_calculated_amount=dep.eis_calculated_amount,
                        eis_approved_amount=dep.eis_approved_amount,
                        eis_initial_replacement_rate=dep.initial_replacement_rate,
                        eis_initial_monthly_amount=dep.eis_initial_monthly_amount,
                        eis_monthly_amount=dep.eis_monthly_amount,
                        month_index=now.month,
                        workforce_employee_dependent=dep,
                        year=now.year,
                        processing_date=date.today(),
                        beneficiary_id=beneficiary_id,
                        is_disbursed=False,
                        payable_amount= dep.eis_monthly_amount,
                        phone_number= dep.phone_number or None
                    )
                    payment_obj.save(username=user.username)
                else:
                    continue


    @transaction.atomic
    def update_beneficiary(self, user, data):
        print(data)
        MIN_ALLOWED_AMOUNT = Decimal("0.00")

        # 1. Fetch Main Beneficiary
        main_beneficiary = WorkforceEisPaymentProcess.objects.filter(
            beneficiary_id=data.get("beneficiary_id"),
            status="active"
        ).first()

        if not main_beneficiary:
            return "Active beneficiary not found"

        # 2. Dates
        event_date = parse_frontend_date(data.get("remarriage_or_death_date")) or date.today()
        today = date.today()

        diff = relativedelta(today, event_date)
        months_elapsed = diff.years * 12 + diff.months
        months_elapsed = months_elapsed if months_elapsed > 0 else 1

        # 3. Parse other beneficiaries
        try:
            other_beneficiaries_input = json.loads(data.get("other_beneficiary_data") or "{}")
        except (json.JSONDecodeError, TypeError):
            return "Invalid other_beneficiary_data JSON"

        # 4. Calculate total overpayment
        actual_monthly_total = safe_decimal(main_beneficiary.eis_monthly_amount)
        target_monthly_total = Decimal("0.00")
        other_beneficiary_records = []

        for b_id, details in other_beneficiaries_input.items():
            other_obj = WorkforceEisPaymentProcess.objects.filter(
                beneficiary_id=b_id,
                status="active"
            ).first()

            if not other_obj:
                continue

            increment = safe_decimal(details.get("incrementAmount"))
            normal_decrement = safe_decimal(details.get("decrementAmount"))
            actual_monthly_total += safe_decimal(other_obj.eis_monthly_amount)
            target_monthly_total += safe_decimal(other_obj.eis_monthly_amount) + increment

            other_beneficiary_records.append({
                "obj": other_obj,
                "increment": increment,
                "normal_decrement": normal_decrement,
            })

        total_overpayment = (actual_monthly_total - target_monthly_total) * Decimal(months_elapsed)
        total_overpayment = max(total_overpayment, Decimal("0.00"))

        # 5. Close main beneficiary (do NOT zero amounts)
        main_beneficiary.status = "inactive"
        main_beneficiary.save(username=user.username)

        main_increment= safe_decimal(data["increment_amount"]) if "increment_amount" in data else 0
        main_decrement= safe_decimal(data["decrement_amount"]) if "decrement_amount" in data else 0

        new_main_row = WorkforceEisPaymentProcess(
            workforce_application=main_beneficiary.workforce_application,
            workforce_application_summary=main_beneficiary.workforce_application_summary,
            workforce_employee_dependent=main_beneficiary.workforce_employee_dependent,
            bank=main_beneficiary.bank,
            bank_account_no=main_beneficiary.bank_account_no,
            bank_account_holder_name=main_beneficiary.bank_account_holder_name,
            eis_payment_type=main_beneficiary.eis_payment_type,
            payment_type_remarks= main_beneficiary.payment_type_remarks,
            eis_calculated_amount=main_beneficiary.eis_calculated_amount,
            eis_approved_amount=main_beneficiary.eis_approved_amount,
            eis_initial_replacement_rate=main_beneficiary.eis_initial_replacement_rate,
            eis_initial_monthly_amount=main_beneficiary.eis_initial_monthly_amount,
            eis_monthly_amount=main_beneficiary.eis_monthly_amount,
            increment_amount= round_three(main_increment) if "increment_amount" in data else None,
            increment_date= today,
            decrement_amount= round_three(main_decrement) if "decrement_amount" in data else None,
            decrement_date= today,
            month_index=main_beneficiary.month_index,
            year=main_beneficiary.year,
            processing_date=today,
            is_disbursed=main_beneficiary.is_disbursed,
            approved=main_beneficiary.approved,
            beneficiary_id=main_beneficiary.beneficiary_id,
            beneficiary_status= data.get("beneficiary_status") if "beneficiary_status" in data else main_beneficiary.beneficiary_status,
            status="active",
            reason=data.get("reason"),
            remarks=data.get("remarks"),
            remarriage_or_death_date=event_date,
            last_live_check_date=parse_frontend_date(data.get("last_live_check_date")),
            live_check_remarks=data.get("live_check_remarks"),
            payable_amount= safe_decimal(main_beneficiary.payable_amount) + main_increment - main_decrement,
            phone_number= main_beneficiary.phone_number or None
        )
        new_main_row.save(username=user.username)

        # 6. Determine decrement_end_date (month-based simulation)
        remaining_overpayment = total_overpayment
        current_month = today
        months_needed = 0

        while remaining_overpayment > 0:
            monthly_capacity = Decimal("0.00")

            for item in other_beneficiary_records:
                old_other = item["obj"]
                increment = item["increment"]
                normal_decrement= item["normal_decrement"]

                max_monthly = safe_decimal(old_other.eis_monthly_amount) + increment
                capacity = max_monthly - MIN_ALLOWED_AMOUNT

                if capacity > 0:
                    monthly_capacity += capacity

            if monthly_capacity <= 0:
                break  # no more recovery possible

            remaining_overpayment -= monthly_capacity
            months_needed += 1

        decrement_end_date = today + relativedelta(months=months_needed)

        # 7. Apply aggressive recovery (single new row per beneficiary)
        remaining_overpayment = total_overpayment

        for item in other_beneficiary_records:
            if remaining_overpayment <= 0:
                break

            old_other = item["obj"]
            increment = item["increment"]

            old_monthly = safe_decimal(old_other.eis_monthly_amount)
            old_initial = safe_decimal(old_other.eis_initial_monthly_amount)

            max_monthly = old_monthly + increment
            max_recoverable = max_monthly - MIN_ALLOWED_AMOUNT

            if max_recoverable <= 0:
                continue

            recovery_amount = min(max_recoverable, remaining_overpayment)

            old_other.status = "inactive"
            try:
                old_other.save(username=user.username)
            except Exception as e:
                continue


            new_other_row=WorkforceEisPaymentProcess(
                workforce_application=old_other.workforce_application,
                workforce_application_summary=old_other.workforce_application_summary,
                workforce_employee_dependent=old_other.workforce_employee_dependent,
                bank=old_other.bank,
                bank_account_no=old_other.bank_account_no,
                bank_account_holder_name=old_other.bank_account_holder_name,
                eis_payment_type=old_other.eis_payment_type,
                payment_type_remarks= old_other.payment_type_remarks,
                eis_calculated_amount=old_other.eis_calculated_amount,
                eis_approved_amount=old_other.eis_approved_amount,
                eis_initial_replacement_rate=old_other.eis_initial_replacement_rate,
                # eis_initial_monthly_amount=(old_initial + increment) - recovery_amount,
                eis_initial_monthly_amount=old_other.eis_initial_monthly_amount,
                eis_monthly_amount=old_other.eis_monthly_amount,
                increment_amount=increment,
                increment_date=event_date,
                decrement_amount=recovery_amount if data.get("beneficiary_status")=="closed" else None,
                decrement_date=today if data.get("beneficiary_status")=="closed" else None,
                decrement_end_date=decrement_end_date if data.get("beneficiary_status")=="closed" else None,
                month_index=old_other.month_index,
                year=old_other.year,
                processing_date=today,
                is_disbursed=old_other.is_disbursed,
                approved=old_other.approved,
                beneficiary_id=old_other.beneficiary_id,
                beneficiary_status=old_other.beneficiary_status,
                status="active",
                reason=old_other.beneficiary_status,
                remarks=old_other.remarks,
                remarriage_or_death_date=old_other.remarriage_or_death_date if data.get("beneficiary_status")=="closed" else None,
                last_live_check_date=old_other.last_live_check_date if data.get("beneficiary_status")=="hold" else None,
                live_check_remarks=old_other.live_check_remarks if data.get("beneficiary_status")=="hold" else None,
                payable_amount= (max_monthly - recovery_amount) if data.get("beneficiary_status")=="closed" else (round_three(old_other.payable_amount + safe_decimal(increment) - safe_decimal(normal_decrement))),
                phone_number= old_other.phone_number or None
            )

            new_other_row.save(username=user.username)

            remaining_overpayment -= recovery_amount

        return "Success"

    def update_payment_by_association(self, user, data):
        try:
            association_id= extract_uuid(data["association_id"])
            increment_percent= safe_decimal(data["increment"]) if "increment" in data else 0
            decrement_percent= safe_decimal(data["decrement"]) if "decrement" in data else 0
            payments= WorkforceEisPaymentProcess.objects.filter(workforce_application__employee_factory__all_association_id=association_id).exclude(beneficiary_status__in=["closed"])

            today = date.today()
            for payment in payments:
                payable_amount= payment.payable_amount
                payment.payable_amount = round_three(safe_decimal(payable_amount) + (safe_decimal(payable_amount) * (increment_percent/100)) - (safe_decimal(payable_amount) * (decrement_percent/100))) if increment_percent>0 or decrement_percent>0 else payable_amount
                payment.increment_amount = round_three(safe_decimal(payable_amount) * (increment_percent/100)) if increment_percent>0 else None
                payment.decrement_amount = round_three(safe_decimal(payable_amount) * (increment_percent/100)) if decrement_percent>0 else None
                payment.increment_date = today if increment_percent>0 else None
                payment.decrement_date = today if decrement_percent>0 else None
                try:
                    payment.save(username=user.username)
                except Exception as e:
                    continue

        except Exception as e:
            return e
