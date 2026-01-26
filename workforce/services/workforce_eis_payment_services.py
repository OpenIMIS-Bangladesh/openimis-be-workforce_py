import logging
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
from decimal import Decimal, InvalidOperation

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
            doctor_json = json.loads(workforce_application.doctors_entry) if workforce_application.doctors_entry else None
            if doctor_json is None:
                return False

            accident_info_json = json.loads(workforce_application.employee_accident_info) if workforce_application.employee_accident_info else None
            if accident_info_json is None:
                return False

            startdate = accident_info_json.get("dateOfRejoining") if accident_info_json.get("dateOfRejoining") else doctor_json.get("dateOfAssessment")
            start_date = datetime.strptime(startdate, "%Y-%m-%d").date() if isinstance(startdate, str) else startdate

            approved_amount = safe_decimal(workforce_application.eis_approved_amount) if workforce_application.eis_approved_amount is not None else 0
            monthly_amount = safe_decimal(workforce_application.eis_monthly_amount) if workforce_application.eis_monthly_amount is not None else 1

            # ---------- CALCULATE MONTHS ----------
            full_months = floor(approved_amount / monthly_amount)
            paid_amount = full_months * monthly_amount
            remaining_amount = round(approved_amount - paid_amount, 2)

            current_date = start_date
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
                    eis_approved_amount=approved_amount,
                    eis_initial_replacement_rate=workforce_application.initial_replacement_rate,
                    eis_initial_monthly_amount=workforce_application.eis_initial_monthly_amount,
                    eis_monthly_amount=monthly_amount,
                    month_index=current_date.month,
                    year=current_date.year,
                    processing_date=date.today(),
                    beneficiary_id=beneficiary_id,
                    is_disbursed=False
                )
                payment_obj.save(username=user.username)
                # for i in range(full_months):
                #     payment_obj= WorkforceEisPaymentProcess(
                #         workforce_application=workforce_application,
                #         bank=bank_instance,
                #         bank_account_no=bank_info[0]["accountNumber"],
                #         bank_account_holder_name=bank_info[0]["accountHolderName"],
                #         eis_payment_type="monthly",
                #         eis_calculated_amount=workforce_application.eis_calculated_amount,
                #         eis_approved_amount=approved_amount,
                #         eis_initial_replacement_rate=workforce_application.initial_replacement_rate,
                #         eis_initial_monthly_amount=workforce_application.eis_initial_monthly_amount,
                #         eis_monthly_amount=monthly_amount,
                #         month_index=current_date.month,
                #         year=current_date.year,
                #         processing_date=date.today(),
                #         beneficiary_id=beneficiary_id,
                #         is_disbursed=False
                #     )
                #     payment_obj.save(username= user.username)
                #     current_date += relativedelta(months=1)
                # # ---------- HANDLE REMAINING AMOUNT ----------
                # if remaining_amount > 0:
                #     payment_obj= WorkforceEisPaymentProcess(
                #         workforce_application=workforce_application,
                #         bank=bank_instance,
                #         bank_account_no=bank_info[0]["accountNumber"],
                #         bank_account_holder_name=bank_info[0]["accountHolderName"],
                #         eis_payment_type="monthly",
                #         eis_calculated_amount=workforce_application.eis_calculated_amount,
                #         eis_approved_amount=approved_amount,
                #         eis_initial_replacement_rate=workforce_application.initial_replacement_rate,
                #         eis_initial_monthly_amount=workforce_application.eis_initial_monthly_amount,
                #         eis_monthly_amount=remaining_amount,  # last partial payment
                #         month_index=current_date.month,
                #         year=current_date.year,
                #         processing_date=date.today(),
                #         beneficiary_id=beneficiary_id,
                #         is_disbursed=False
                #     )
                #     payment_obj.save(username= user.username)
            return None
        else:
            accident_info_json = json.loads(workforce_application.employee_accident_info) if workforce_application.employee_accident_info else None
            if accident_info_json is None:
                return False

            startdate = accident_info_json.get("dateOfDeath") if accident_info_json.get("dateOfDeath") else None
            start_date = datetime.strptime(startdate, "%Y-%m-%d").date() if isinstance(startdate, str) else startdate
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


                    approved_amount = safe_decimal(dep.eis_approved_amount)
                    monthly_amount = safe_decimal(dep.eis_monthly_amount)

                    # ---------- CALCULATE MONTHS ----------
                    full_months = floor(approved_amount / monthly_amount)
                    paid_amount = full_months * monthly_amount
                    remaining_amount = round(approved_amount - paid_amount, 2)

                    current_date = start_date
                    payment_obj = WorkforceEisPaymentProcess(
                        workforce_application=workforce_application,
                        bank=bank_instance,
                        bank_account_no=dep.bank_account_no,
                        bank_account_holder_name=dep.bank_account_holder_name,
                        eis_payment_type="monthly",
                        eis_calculated_amount=dep.eis_calculated_amount,
                        eis_approved_amount=approved_amount,
                        eis_initial_replacement_rate=dep.initial_replacement_rate,
                        eis_initial_monthly_amount=dep.eis_initial_monthly_amount,
                        eis_monthly_amount=monthly_amount,
                        month_index=current_date.month,
                        workforce_employee_dependent=dep,
                        year=current_date.year,
                        processing_date=date.today(),
                        beneficiary_id=beneficiary_id,
                        is_disbursed=False
                    )
                    payment_obj.save(username=user.username)

                    # for i in range(full_months):
                    #     payment_obj= WorkforceEisPaymentProcess(
                    #         workforce_application=workforce_application,
                    #         bank=bank_instance,
                    #         bank_account_no=dep.bank_account_no,
                    #         bank_account_holder_name=dep.bank_account_holder_name,
                    #         eis_payment_type="monthly",
                    #         eis_calculated_amount=dep.eis_calculated_amount,
                    #         eis_approved_amount=approved_amount,
                    #         eis_initial_replacement_rate = dep.initial_replacement_rate,
                    #         eis_initial_monthly_amount=dep.eis_initial_monthly_amount,
                    #         eis_monthly_amount=monthly_amount,
                    #         month_index=current_date.month,
                    #         workforce_employee_dependent=dep,
                    #         year=current_date.year,
                    #         processing_date=date.today(),
                    #         beneficiary_id=beneficiary_id,
                    #         is_disbursed=False
                    #     )
                    #     payment_obj.save(username= user.username)
                    #     current_date += relativedelta(months=1)
                    # # ---------- HANDLE REMAINING AMOUNT ----------
                    # if remaining_amount > 0:
                    #     payment_obj= WorkforceEisPaymentProcess(
                    #         workforce_application=workforce_application,
                    #         bank=bank_instance,
                    #         bank_account_no=dep.bank_account_no,
                    #         bank_account_holder_name=dep.bank_account_holder_name,
                    #         eis_payment_type="monthly",
                    #         eis_calculated_amount=dep.eis_calculated_amount,
                    #         eis_approved_amount=approved_amount,
                    #         eis_initial_replacement_rate=dep.initial_replacement_rate,
                    #         eis_initial_monthly_amount=dep.eis_initial_monthly_amount,
                    #         eis_monthly_amount=remaining_amount,  # last partial payment
                    #         month_index=current_date.month,
                    #         workforce_employee_dependent=dep,
                    #         year=current_date.year,
                    #         processing_date=date.today(),
                    #         beneficiary_id=beneficiary_id,
                    #         is_disbursed=False
                    #     )
                    #     payment_obj.save(username= user.username)
                    #
                else:
                    continue


    def update_beneficiary(self, user, data):
        beneficiary= WorkforceEisPaymentProcess.objects.filter(beneficiary_id= data['beneficiary_id'], status="active").first()
        if not beneficiary:
            return "Active beneficiary not found"
        new_row = WorkforceEisPaymentProcess(
                    workforce_application= beneficiary.workforce_application,
                    workforce_application_summary = beneficiary.workforce_application_summary,
                    workforce_employee_dependent = beneficiary.workforce_employee_dependent,
                    bank = beneficiary.bank,
                    bank_account_no = beneficiary.bank_account_no,
                    bank_account_holder_name = beneficiary.bank_account_holder_name,
                    eis_payment_type = beneficiary.eis_payment_type,
                    eis_calculated_amount = beneficiary.eis_calculated_amount,
                    eis_approved_amount = beneficiary.eis_approved_amount,
                    eis_initial_replacement_rate = beneficiary.eis_initial_replacement_rate,
                    eis_initial_monthly_amount = beneficiary.eis_initial_monthly_amount + safe_decimal(data["increment_amount"]) - safe_decimal(data["decrement_amount"]),
                    eis_monthly_amount = safe_decimal(beneficiary.eis_monthly_amount) + safe_decimal(data["increment_amount"]) - safe_decimal(data["decrement_amount"]),
                    increment_amount = safe_decimal(data["increment_amount"]),
                    increment_date = data['increment_date'] if data["increment_date"]!="" else None,
                    decrement_amount = safe_decimal(data["decrement_amount"]),
                    decrement_date = data['decrement_date'] if data['decrement_date']!="" else None,
                    month_index = beneficiary.month_index,
                    year = beneficiary.year,
                    processing_date = date.today(),
                    is_disbursed = beneficiary.is_disbursed,
                    approved = beneficiary.approved,
                    beneficiary_id = beneficiary.beneficiary_id,
                    beneficiary_status = data["beneficiary_status"],
                    reason = data["reason"],
                    remarks = data["remarks"],
                    remarriage_or_death_date = data["remarriage_or_death_date"],
                    last_live_check_date = data["last_live_check_date"] or None,
                    live_check_remarks = data["remarks"] or None,
                )

        try:
            new_row.save(username=user.username)
            try:
                beneficiary.status= "inactive"
                beneficiary.save(username=user.username)
                try:
                    other_beneficiaries = json.loads(data.get('other_beneficiary_data') or "{}")
                except json.JSONDecodeError:
                    return "Invalid beneficiary JSON"

                if other_beneficiaries is not None:
                    month_diff= calculate_age_in_months(beneficiary.remarriage_or_death_date)
                    initial_monthly_amount_total = safe_decimal(beneficiary.eis_initial_monthly_amount) / (month_diff if month_diff>0 else 1)
                    monthly_amount_total = safe_decimal(beneficiary.eis_monthly_amount) / (month_diff if month_diff>0 else 1)
                    beneficiary_count= len(other_beneficiaries)
                    decrement_amount= monthly_amount_total / beneficiary_count
                    if other_beneficiaries:
                        for beneficiary_id, details in other_beneficiaries.items():
                            increment_amount = int(details["incrementAmount"])
                            increment_date = details["incrementDate"]
                            other_beneficiary = WorkforceEisPaymentProcess.objects.filter(
                            beneficiary_id=beneficiary_id, status="active").first()
                            new_row = WorkforceEisPaymentProcess(
                                workforce_application=other_beneficiary.workforce_application,
                                workforce_application_summary=other_beneficiary.workforce_application_summary,
                                workforce_employee_dependent=other_beneficiary.workforce_employee_dependent,
                                bank=other_beneficiary.bank,
                                bank_account_no=other_beneficiary.bank_account_no,
                                bank_account_holder_name=other_beneficiary.bank_account_holder_name,
                                eis_payment_type=other_beneficiary.eis_payment_type,
                                eis_calculated_amount=other_beneficiary.eis_calculated_amount,
                                eis_approved_amount=other_beneficiary.eis_approved_amount,
                                eis_initial_replacement_rate=other_beneficiary.eis_initial_replacement_rate,
                                eis_initial_monthly_amount=other_beneficiary.eis_initial_monthly_amount,
                                eis_monthly_amount=safe_decimal(other_beneficiary.eis_monthly_amount) + safe_decimal(increment_amount) - safe_decimal(decrement_amount),
                                increment_amount=safe_decimal(increment_amount),
                                increment_date=increment_date if increment_date != "" else None,
                                decrement_amount=safe_decimal(decrement_amount),
                                decrement_date=date.today(),
                                month_index=other_beneficiary.month_index,
                                year=other_beneficiary.year,
                                processing_date=date.today(),
                                is_disbursed=other_beneficiary.is_disbursed,
                                approved=other_beneficiary.approved,
                                beneficiary_id=beneficiary_id,
                                beneficiary_status=other_beneficiary.beneficiary_status,
                                reason=other_beneficiary.reason,
                                remarks="Amount adjusted for other beneficiary's death or remarriage",
                                remarriage_or_death_date=other_beneficiary.remarriage_or_death_date,
                                last_live_check_date=other_beneficiary.last_live_check_date or None,
                                live_check_remarks=data["remarks"] or None,
                            )
                            try:
                                new_row.save(username=user.username)
                                other_beneficiary.status= "inactive"
                                try:
                                    other_beneficiary.save(username=user.username)
                                except Exception as e:
                                    return e
                            except Exception as e:
                                return e

            except Exception as e:
                return e
        except Exception as e:
            return e

        return
