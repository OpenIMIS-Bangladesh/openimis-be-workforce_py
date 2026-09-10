import logging
from xmlrpc.client import DateTime

from core.services import BaseService

from workforce.models import WorkforceEmployeeDependent, WorkforceApplication, WorkforceEmployee, WorkforceFactory, \
    WorkforceAllAssociation, WorkforceOtherCompensationInfo
from datetime import datetime, timezone, date
import requests
import json
import os
from django.db.models import Sum

logger = logging.getLogger(__name__)


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class WorkforceEmployeeDependentServices(BaseService):
    OBJECT_TYPE = WorkforceEmployeeDependent

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)

    def get_gender_by_relation(self, relation_with_worker):
        if relation_with_worker == "workforce.relation.father" or relation_with_worker == "workforce.relation.son" or relation_with_worker == "workforce.relation.husband" or relation_with_worker == "workforce.relation.brother" or relation_with_worker == "workforce.relation.grand_father" or relation_with_worker == "workforce.relation.grand_son":
            return "male"
        else:
            return "female"

    def get_gender_by_relation_for_api(self, relation_with_worker):
        if relation_with_worker == "workforce.relation.father" or relation_with_worker == "workforce.relation.son" or relation_with_worker == "workforce.relation.husband" or relation_with_worker == "workforce.relation.brother" or relation_with_worker == "workforce.relation.grand_father" or relation_with_worker == "workforce.relation.grand_son":
            return "Male"
        else:
            return "Female"

    def get_relation_for_api(self, dep_obj, worker_age, calculation_start_date=None):
        age = self.calculate_age_custom(dep_obj.birth_date, calculation_start_date)

        relation = dep_obj.relation_with_worker
        marital = dep_obj.marital_status
        disability = dep_obj.disability_status

        #GLOBAL RULE (same as JS)
        # if (
        #         relation != "workforce.relation.wife"
        #         and age < 18
        #         and marital == "workforce.marital_status.married"
        # ):
        #     return None

        # Wife
        if relation == "workforce.relation.wife":
            if age >= 16 and marital == "workforce.marital_status.widow":
                return "Widow"
            return None

        # Husband
        elif relation == "workforce.relation.husband":
            if age > 18 and marital == "workforce.marital_status.widower":
                return "Dependent widower"
            return None

        # Son
        elif relation == "workforce.relation.son":
            if age < 18:
                return "Minor son"
            if age >= 18 and disability == "yes":
                return "Dependent disabled son"
            return None

        # Daughter
        elif relation == "workforce.relation.daughter":
            if marital == "workforce.marital_status.married" or marital == "workforce.marital_status.widow":
                return None
            return "Unmarried daughter"

        # Brother
        elif relation == "workforce.relation.brother":
            if age < 18:
                return "Dependent minor brother"
            return None

        # Sister
        elif relation == "workforce.relation.sister":
            if marital == "workforce.marital_status.married" or marital == "workforce.marital_status.widow":
                return None
            return "Dependent unmarried sister"

        # Father
        elif relation == "workforce.relation.father":
            if age > worker_age:
                return "Dependent father"
            return None

        # Mother
        elif relation == "workforce.relation.mother":
            if age > worker_age:
                return "Mother"
            return None

        # Grand parents
        elif relation == "workforce.relation.grand_father":
            return "Dependent paternal grandfather"

        elif relation == "workforce.relation.grand_mother":
            return "Dependent paternal grandmother"

        # Grand children (all age < 18)
        elif relation in (
                "workforce.relation.grand_son",
                "workforce.relation.grand_son_from_daughter",
        ):
            if age < 18:
                return "Dependent minor grandson"
            return None

        elif relation in (
                "workforce.relation.grand_daughter",
                "workforce.relation.grand_daughter_from_daughter",
        ):
            if age < 18:
                return "Dependent minor granddaughter"
            return None

        # Daughter in law
        elif relation == "workforce.relation.daughter_in_law":
            if marital == "workforce.marital_status.widowed":
                return "Dependent widowed daughter-in-law"
            return None

        # Illegitimate children
        elif relation == "workforce.relation.illegitimate_son":
            return "Dependent son born out of wedlock"

        elif relation == "workforce.relation.illegitimate_daughter":
            if marital == "workforce.marital_status.unmarried":
                return "Dependent unmarried daughter born out of wedlock"
            return None

        return None

    def calculate_age(self, birth_date):
        if not birth_date:
            return None

        if isinstance(birth_date, str):
            try:
                dob = datetime.strptime(birth_date, "%Y-%m-%d %H:%M:%S.%f %z")
            except ValueError:
                try:
                    dob = datetime.strptime(birth_date, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    dob = datetime.strptime(birth_date, "%Y-%m-%d")
        elif isinstance(birth_date, date):
            dob = datetime.combine(birth_date, datetime.min.time())
        else:
            dob = birth_date  # already a datetime

        now = datetime.now(timezone.utc)
        age = now.year - dob.year - ((now.month, now.day) < (dob.month, dob.day))
        return age

    def calculate_age_custom(self, birth_date, date_for_calculation=None):
        if not birth_date:
            return None

        if isinstance(birth_date, str):
            try:
                dob = datetime.strptime(birth_date, "%Y-%m-%d %H:%M:%S.%f %z")
            except ValueError:
                try:
                    dob = datetime.strptime(birth_date, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    dob = datetime.strptime(birth_date, "%Y-%m-%d")
        elif isinstance(birth_date, date):
            dob = datetime.combine(birth_date, datetime.min.time())
        else:
            dob = birth_date  # already a datetime

        if date_for_calculation:
            if isinstance(date_for_calculation, str):
                try:
                    ref_date = datetime.strptime(date_for_calculation, "%Y-%m-%d %H:%M:%S.%f %z")
                except ValueError:
                    try:
                        ref_date = datetime.strptime(date_for_calculation, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        ref_date = datetime.strptime(date_for_calculation, "%Y-%m-%d")
            elif isinstance(date_for_calculation, date):
                ref_date = datetime.combine(date_for_calculation, datetime.min.time())
            else:
                ref_date = date_for_calculation
        else:
            ref_date = datetime.now(timezone.utc)

        age = ref_date.year - dob.year - (
                (ref_date.month, ref_date.day) < (dob.month, dob.day)
        )
        return age

    def calculate_days(self, start_date, end_date=None):
        if not start_date:
            return None

        # -------------------------
        # Parse start_date
        # -------------------------
        if isinstance(start_date, str):
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S.%f %z")
            except ValueError:
                try:
                    start = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    start = datetime.strptime(start_date, "%Y-%m-%d")

        elif isinstance(start_date, date):
            start = datetime.combine(start_date, datetime.min.time())

        else:
            start = start_date  # already datetime

        # -------------------------
        # Parse end_date
        # -------------------------
        if end_date:
            if isinstance(end_date, str):
                try:
                    end = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S.%f %z")
                except ValueError:
                    try:
                        end = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        end = datetime.strptime(end_date, "%Y-%m-%d")

            elif isinstance(end_date, date):
                end = datetime.combine(end_date, datetime.min.time())

            else:
                end = end_date
        else:
            end = datetime.now(timezone.utc)

        # -------------------------
        # Calculate difference in days
        # -------------------------
        if start.tzinfo and end.tzinfo:
            delta = end - start
        else:
            delta = end.replace(tzinfo=None) - start.replace(tzinfo=None)

        return delta.days


    def update_eligibility(self, workforce_application_id):
        try:
            dependents = WorkforceEmployeeDependent.objects.filter(workforce_application_id=workforce_application_id)
            for dependent in dependents:
                dep_obj = WorkforceEmployeeDependent.objects.get(id=dependent.id)
                relation = dep_obj.relation_with_worker
                gender = self.get_gender_by_relation(relation)
                eligible = False

                # FEMALE RELATIONSHIPS
                if gender == "female":
                    if relation == "workforce.relation.mother":
                        # Mother: check if alive
                        if dep_obj.life_status == "alive":
                            eligible = True
                        else:
                            eligible = False

                    elif relation in ["workforce.relation.wife", "workforce.relation.sister",
                                      "workforce.relation.daughter"]:
                        # Wife/Sister/Daughter: check if married
                        if not dep_obj.marital_status == "married":
                            eligible = True
                        else:
                            eligible = False

                # MALE RELATIONSHIPS
                elif gender == "male":
                    if relation == "workforce.relation.father":
                        # Father: check if alive
                        if dep_obj.life_status == "alive":
                            eligible = True
                        else:
                            eligible = False

                    elif relation in ["workforce.relation.son", "workforce.relation.brother"]:
                        # Son/Brother: check if physically challenged, then alive
                        if dep_obj.disability_status == "yes":
                            if dep_obj.life_status == "alive":
                                eligible = True
                            else:
                                eligible = False
                        else:
                            eligible = False

                    elif relation == "workforce.relation.husband":
                        # Husband: check if newly married
                        if dep_obj.marital_status == "married":
                            eligible = False
                        else:
                            eligible = True

                # Finally save7
                dep_obj.is_eligible = eligible
                try:
                    dep_obj.save(username=self.user.username)
                except Exception as e:
                    continue
            return {"status": True, "error": ""}
        except Exception as e:
            return {"status": False, "error": str(e)}

    def calculate_eis_amount(self, workforce_application_id, application_type):
        dependents = WorkforceEmployeeDependent.objects.filter(workforce_application_id=workforce_application_id)
        workforce_application = WorkforceApplication.objects.get(id=workforce_application_id)
        worker = WorkforceEmployee.objects.get(id=workforce_application.workforce_employee_id)




        # metadata_json= workforce_application.metadata
        # metadata= json.loads(metadata_json)
        calculation_start_date= ""
        date_for_worker_age_calculation=""
        if workforce_application.application_type == "disabilityAssistance":
            doctor_json = json.loads(workforce_application.doctors_entry) if workforce_application.doctors_entry else None
            if doctor_json is None:
                return False
            disability_percentage = doctor_json.get("disabilityPerSchedule") if "disabilityPerSchedule" in doctor_json else "0"
            accident_info_json = json.loads(
                workforce_application.employee_accident_info) if workforce_application.employee_accident_info else None
            if accident_info_json is None:
                return False

            calculation_start_date = accident_info_json.get("dateOfRejoining") if accident_info_json.get("dateOfRejoining") else doctor_json.get("dateOfAssessment")
            calculation_start_date = datetime.strptime(calculation_start_date, "%Y-%m-%d").date() if isinstance(calculation_start_date, str) else calculation_start_date
        else:
            accident_info_json = json.loads(
                workforce_application.employee_accident_info) if workforce_application.employee_accident_info else None
            if accident_info_json is None:
                return False
            calculation_start_date = accident_info_json.get("dateOfDeath") if accident_info_json.get("dateOfDeath") else None
            calculation_start_date = datetime.strptime(calculation_start_date, "%Y-%m-%d").date() if isinstance(calculation_start_date, str) else calculation_start_date
            disability_percentage = "100"


        # Calculate age
        date_for_worker_age_calculation = accident_info_json.get("accidentDate") if accident_info_json.get("accidentDate") else doctor_json.get("dateOfAssessment")
        date_for_worker_age_calculation = datetime.strptime(date_for_worker_age_calculation, "%Y-%m-%d").date() if isinstance(date_for_worker_age_calculation, str) else date_for_worker_age_calculation
        worker_age = self.calculate_age_custom(worker.birth_date, date_for_worker_age_calculation)
        if workforce_application=="financialAssistance":
            deceased_worker_info= json.loads(workforce_application.deceased_worker_info) if workforce_application.deceased_worker_info else None
            if deceased_worker_info is not None and deceased_worker_info!="[{}]":
                worker_dob= deceased_worker_info.get("birthDate", None)
                worker_age= self.calculate_age_custom(worker_dob, calculation_start_date) if worker_dob else 0
        dependents = list(dependents)  # evaluate queryset once
        dependents = [
            dep for dep in dependents
            if self.get_relation_for_api(dep,worker_age, calculation_start_date) and dep.is_eligible == True and dep.bank_id is not None
        ]
        last_base_salary = float(workforce_application.last_base_salary.replace(",","")) if workforce_application.last_base_salary else 0
        factory = WorkforceFactory.objects.get(id=workforce_application.employee_factory.id)
        association= WorkforceAllAssociation.objects.get(id= factory.all_association_id)
        minimum_salary= association.minimum_salary or 0
        # minimum_salary = 12500
        maximum_salary = minimum_salary * 4
        if last_base_salary <= maximum_salary:
            salary_parameter = last_base_salary
        elif last_base_salary == 85000:
            salary_parameter = 85000
        else:
            salary_parameter = maximum_salary

        total_other_payment = (
                                  WorkforceOtherCompensationInfo.objects
                                  .filter(
                                      workforce_application_id=workforce_application_id,
                                      is_eis_benefit_adjustment_eligible="true"
                                  )
                                  .aggregate(total=Sum('amount'))
                              )['total'] or 0
        payload = {
            "parameters": {
                "Interest rate": "8.1%",
                "Indexation rate": "6%",
                "Date of accident": calculation_start_date.strftime("%m/%d/%Y") if calculation_start_date else "08/08/2024",
                "Date of calculation": calculation_start_date.strftime("%m/%d/%Y") if calculation_start_date else "08/08/2024",
                # "Date of calculation": datetime.now(timezone.utc).strftime("%m/%d/%Y"),
                "Payment from Central Fund": total_other_payment
            },
            "Worker": {
                "Name": worker.first_name_en,
                "ID": str(worker.id),
                "Status": "Disabled" if application_type == "disabilityAssistance" else "Deceased",
                "Disability level": disability_percentage + ("" if disability_percentage is not None and "%" in disability_percentage else "%"),
                # "Disability level": "50%",
                "Monthly earnings used for calculation": str(salary_parameter),
                "Date of birth": worker.birth_date.strftime("%m/%d/%Y") if worker.birth_date else "10/16/1997",
                "Age at calculation date": str(worker_age or 26),
                "Sex": "Male" if worker.gender == "workforce.gender.male" or worker.gender == "M" else "Female"
            },
            "Number of dependents": str(len(dependents)),
            "Dependents": []
        }

        # Loop over dependents
        dep_key = 1
        for dep in dependents:
            payload["Dependents"].append({
                "Name": dep.name_en or dep.name_bn or "",
                # "ID": str(dep.id),
                "ID": str(dep_key),
                "Date of birth": dep.birth_date.strftime("%m/%d/%Y") if dep.birth_date else "11/02/1996",
                "Age at calculation date": str(self.calculate_age_custom(dep.birth_date, calculation_start_date)) if dep.birth_date else "30",
                "Sex": self.get_gender_by_relation_for_api(dep.relation_with_worker) or "Female",
                "Relationship": self.get_relation_for_api(dep, worker_age, calculation_start_date) or "",
                "nid": dep.nid

            })
            dep_key = dep_key + 1

        # === API CALL ===
        vba_data = []
        try:
            endpoint = os.environ.get("CALCULATION_API_URL")
            response = requests.post(endpoint, json=payload, timeout=360)
            if response.status_code == 200:
                vba_response = response.json()
                if application_type == 'disabilityAssistance':
                    vba_data = vba_response["data"]["results"][0]
                    worker_pv_factor = vba_data.get("PV factor")
                    worker_calculated_amount = vba_data.get("PV Total pension")
                    worker_approved_amount = vba_data.get("PV Top-Up pension")
                    worker_initial_replacement_rate = vba_data.get("Initial replacement rate")
                    worker_initial_monthly_amount = vba_data.get("Total initial monthly pension")
                    worker_monthly_amount = vba_data.get("Top-up monthly pension")

                    workforce_application.eis_calculated_amount = worker_calculated_amount
                    workforce_application.eis_approved_amount = worker_approved_amount
                    workforce_application.eis_initial_monthly_amount = worker_initial_monthly_amount
                    workforce_application.eis_monthly_amount = worker_monthly_amount
                    workforce_application.pv_factor = worker_pv_factor
                    workforce_application.initial_replacement_rate = worker_initial_replacement_rate
                    workforce_application.save(username=self.user.username)
                else:
                    vba_data = vba_response["data"]["results"]

                # Example: Extract disability amount and payment details

            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return

        except Exception as e:
            print(f"Error calling VBA API: {e}")
            return

        if application_type == "financialAssistance":
            for dependent in dependents:
                dep_obj = WorkforceEmployeeDependent.objects.get(id=dependent.id)
                age = self.calculate_age_custom(dep_obj.birth_date, calculation_start_date)

                dep_data_for_check = {}

                total_amount = 0
                top_up_amount = 0
                pv_factor = 0
                initial_replacement_rate = 0
                initial_monthly_amount = 0
                monthly_amount = 0

                # find dependent data in payload
                for dep_data in payload["Dependents"]:
                    if dep_data["Name"] == dep_obj.name_en and dep_data["nid"] == dep_obj.nid:
                        dep_data_for_check = dep_data
                        break

                relation = str(dep_obj.relation_with_worker).lower()

                # -------- PARENT LOGIC --------
                if "workforce.relation.father" in relation or "workforce.relation.mother" in relation:

                    father_present = False
                    mother_present = False

                    for thisdata in vba_data:
                        relationship = str(thisdata.get("Relationship", "")).lower()

                        if "mother" in relationship:
                            mother_present = True

                        if "dependent father" in relationship:
                            father_present = True

                    # get parent data
                    parent_data = None
                    for row in vba_data:
                        if row.get("ID") == "Parent(s)":
                            parent_data = row
                            break

                    if parent_data:
                        total_amount = safe_float(parent_data["PV Total pension"])
                        top_up_amount = safe_float(parent_data["PV Top-Up pension"])
                        pv_factor = safe_float(parent_data["PV factor"])
                        initial_replacement_rate = safe_float(parent_data["Initial replacement rate"])
                        initial_monthly_amount = safe_float(parent_data["Total initial monthly pension"])
                        monthly_amount = safe_float(parent_data["Top-up monthly pension"])

                    # if both parents exist split
                    if mother_present and father_present:
                        total_amount /= 2
                        top_up_amount /= 2
                        pv_factor /= 2
                        initial_replacement_rate /= 2
                        initial_monthly_amount /= 2
                        monthly_amount /= 2

                    dep_obj.eis_calculated_amount = total_amount
                    dep_obj.eis_approved_amount = top_up_amount
                    dep_obj.pv_factor = pv_factor
                    dep_obj.initial_replacement_rate = initial_replacement_rate
                    dep_obj.eis_initial_monthly_amount = initial_monthly_amount
                    dep_obj.eis_monthly_amount = monthly_amount
                    dep_obj.is_eligible = True

                # -------- OTHER DEPENDENTS --------
                else:
                    for data in vba_data:

                        try:
                            if int(data.get("ID")) != int(dep_data_for_check.get("ID")):
                                continue
                        except (TypeError, ValueError):
                            continue

                        relationship = str(data.get("Relationship", "")).lower()

                        if (
                                data.get("Relationship") in ["Widow", "Dependent widower"]
                                or "son" in relationship
                                or "daughter" in relationship
                        ):

                            for spouse_orphan in vba_data:
                                if spouse_orphan.get("ID") == "Spouse(s) and Orphan(s)":
                                    total_amount = safe_float(spouse_orphan["PV Total pension"])
                                    top_up_amount = safe_float(spouse_orphan["PV Top-Up pension"])

                                    dep_obj.eis_calculated_amount = total_amount * safe_float(
                                        data["Initial replacement rate"])
                                    dep_obj.eis_approved_amount = top_up_amount * safe_float(
                                        data["Initial replacement rate"])
                                    dep_obj.pv_factor = safe_float(data["PV factor"])
                                    dep_obj.initial_replacement_rate = safe_float(data["Initial replacement rate"])
                                    dep_obj.eis_initial_monthly_amount = safe_float(
                                        data["Total initial monthly pension"])
                                    dep_obj.eis_monthly_amount = safe_float(data["Top-up monthly pension"])
                                    dep_obj.is_eligible = True
                                    break

                        else:
                            dep_obj.eis_calculated_amount = safe_float(data["PV Total pension"])
                            dep_obj.eis_approved_amount = safe_float(data["PV Top-Up pension"])
                            dep_obj.pv_factor = safe_float(data["PV factor"])
                            dep_obj.initial_replacement_rate = safe_float(data["Initial replacement rate"])
                            dep_obj.eis_initial_monthly_amount = safe_float(data["Total initial monthly pension"])
                            dep_obj.eis_monthly_amount = safe_float(data["Top-up monthly pension"])
                            dep_obj.is_eligible = True

                try:
                    dep_obj.save(username=self.user.username)
                except Exception:
                    continue

        return None



