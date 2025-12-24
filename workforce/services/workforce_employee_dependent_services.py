import logging
import json
from core.services import BaseService
from pamqp.decode import double

from workforce.models import WorkforceEmployeeDependent, WorkforceApplication, WorkforceEmployee, WorkforceFactory, \
    WorkforceAllAssociation
from datetime import datetime, timezone, date
import requests
import json
import os

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
        if relation_with_worker=="workforce.relation.father" or relation_with_worker=="workforce.relation.son" or relation_with_worker=="workforce.relation.husband" or relation_with_worker=="workforce.relation.brother" or relation_with_worker=="workforce.relation.grand_father" or relation_with_worker=="workforce.relation.grand_son":
            return "male"
        else:
            return "female"

    def get_gender_by_relation_for_api(self, relation_with_worker):
        if relation_with_worker=="workforce.relation.father" or relation_with_worker=="workforce.relation.son" or relation_with_worker=="workforce.relation.husband" or relation_with_worker=="workforce.relation.brother" or relation_with_worker=="workforce.relation.grand_father" or relation_with_worker=="workforce.relation.grand_son":
            return "Male"
        else:
            return "Female"

    def get_relation_for_api(self, dep_obj):
        age = self.calculate_age(dep_obj.birth_date)


        relation = dep_obj.relation_with_worker
        marital = dep_obj.marital_status
        disability = dep_obj.disability_status

        # --- Relation-wise Eligibility ---
        if relation == "workforce.relation.brother":
            if age < 18:
                return "Dependent minor brother"

        elif relation == "workforce.relation.sister":
            if age < 18:
                return "Dependent minor sister"
            elif marital == "workforce.marital_status.unmarried":
                return "Dependent unmarried sister"
            elif marital == "workforce.marital_status.widowed":
                return "Dependent widowed sister"

        elif relation == "workforce.relation.daughter":
            if disability == "yes":
                return "Dependent disabled daughter"
            elif marital == "workforce.marital_status.unmarried":
                return "Unmarried daughter"
            elif marital == "workforce.marital_status.widowed":
                return "Dependent widowed daughter"
            elif age < 18:
                return "Minor daughter"

        elif relation == "workforce.relation.son":
            if disability == "yes":
                return "Dependent disabled son"
            elif age < 18:
                return "Minor son"

        elif relation == "workforce.relation.husband":
            return "Dependent widower"

        elif relation == "workforce.relation.wife":
            return "Widow"

        elif relation == "workforce.relation.father":
            return "Dependent father"

        elif relation == "workforce.relation.mother":
            return "Mother"

        elif relation == "workforce.relation.grand_father":
            return "Dependent paternal grandfather"

        elif relation == "workforce.relation.grand_monther":
            return "Dependent paternal grandmother"

        elif relation == "workforce.relation.grand_son":
            if age < 18:
                return "Dependent minor son of a deceased son"

        elif relation == "workforce.relation.grand_daughter":
            if age < 18:
                return "Dependent minor daughter of a deceased son"

        elif relation == "workforce.relation.daughter_in_law":
            if marital == "workforce.marital_status.widowed":
                return "Dependent widowed daughter-in-law"

        elif relation == "workforce.relation.illegitimate_son":
            return "Dependent son born out of wedlock"

        elif relation == "workforce.relation.illegitimate_daughter":
            if marital == "workforce.marital_status.unmarried":
                return "Dependent unmarried daughter born out of wedlock"

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



    def update_eligibility(self, workforce_application_id):
        try:
            dependents= WorkforceEmployeeDependent.objects.filter(workforce_application_id=workforce_application_id)
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
                        if dep_obj.disability_status=="yes":
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
                dep_obj.save(username=self.user.username)
            return {"status": True, "error": ""}
        except Exception as e:
            return {"status": False, "error": str(e)}

    def calculate_eis_amount(self, workforce_application_id, application_type):
        dependents = WorkforceEmployeeDependent.objects.filter(workforce_application_id=workforce_application_id)
        dependents = list(dependents)  # evaluate queryset once
        dependents = [
            dep for dep in dependents
            if self.get_relation_for_api(dep)
        ]

        workforce_application= WorkforceApplication.objects.get(id= workforce_application_id)
        worker= WorkforceEmployee.objects.get(id= workforce_application.workforce_employee_id)


        # Calculate age
        worker_age = self.calculate_age(worker.birth_date)

        # metadata_json= workforce_application.metadata
        # metadata= json.loads(metadata_json)
        doctor_data = json.loads(workforce_application.doctors_entry) if workforce_application.doctors_entry else None
        if doctor_data:
            disability_percentage = doctor_data.get("disabilityPerSchedule")
        else:
            if application_type == "financialAssistance":
                disability_percentage = "100"
            else:
                disability_percentage = "0"

        last_base_salary = float(workforce_application.last_base_salary) if workforce_application.last_base_salary else 0
        factory= WorkforceFactory.objects.get(id= workforce_application.employee_factory.id)
        association= WorkforceAllAssociation.objects.get(id= factory.all_association_id)
        minimum_salary= association.minimum_salary or 0
        maximum_salary= minimum_salary*4
        if last_base_salary <= maximum_salary:
            salary_parameter= last_base_salary
        else:
            salary_parameter= maximum_salary

        payload = {
            "parameters": {
                "Interest rate": "8.1%",
                "Indexation rate": "6%",
                "Date of accident": workforce_application.date_created.strftime(
                    "%m/%d/%Y") if workforce_application.date_created else "08/08/2024",
                "Date of calculation": workforce_application.date_created.strftime(
                    "%m/%d/%Y") if workforce_application.date_created else "08/26/2024",
                "Payment from Central Fund": "200000"
            },
            "Worker": {
                "Name": worker.first_name_en,
                "ID": str(worker.id),
                "Status": "Disabled" if application_type=="disabilityAssistance" else "Deceased",
                "Disability level": disability_percentage+("" if "%" in disability_percentage else "%"),
                # "Disability level": "50%",
                "Monthly earnings used for calculation": str(salary_parameter),
                "Date of birth": worker.birth_date.strftime(
                    "%m/%d/%Y") if worker.birth_date else "10/16/1997",
                "Age at calculation date": str(worker_age or 26),
                "Sex": "Male" if worker.gender=="workforce.gender.male" or worker.gender=="M" else "Female"
            },
            "Number of dependents": str(len(dependents)),
            "Dependents": []
        }

        # Loop over dependents
        dep_key=1
        for dep in dependents:
            payload["Dependents"].append({
                "Name": dep.name_en or dep.name_bn or "",
                # "ID": str(dep.id),
                "ID": str(dep_key),
                "Date of birth": dep.birth_date.strftime("%m/%d/%Y") if dep.birth_date else "11/02/1996",
                "Age at calculation date": str(self.calculate_age(dep.birth_date)) if dep.birth_date else "30",
                "Sex": self.get_gender_by_relation_for_api(dep.relation_with_worker) or "Female",
                "Relationship": self.get_relation_for_api(dep) or ""
            })
            dep_key= dep_key+1

        # === API CALL ===
        vba_data = []
        try:
            endpoint = os.environ.get("CALCULATION_API_URL")
            response = requests.post(endpoint, json=payload, timeout=360)
            if response.status_code == 200:
                vba_response = response.json()
                if application_type=='disabilityAssistance':
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
                age= self.calculate_age(dep_obj.birth_date)

                # Helper to assign VBA data to dependent
                def set_vba_data(dep_obj, rel):
                    for data in vba_data:
                        if data["Relationship"] == rel:
                            if rel== "Mother" or rel =="Dependent father":
                                for parent_data in vba_data:
                                    if parent_data["ID"] == "Parent(s)":
                                        dep_obj.eis_calculated_amount = safe_float(parent_data["PV Total pension"])/2
                                        dep_obj.eis_approved_amount = safe_float(parent_data["PV Top-Up pension"])/2
                                        dep_obj.pv_factor = safe_float(parent_data["PV factor"])
                                        dep_obj.initial_replacement_rate = safe_float(parent_data["Initial replacement rate"])/2
                                        dep_obj.eis_initial_monthly_amount = safe_float(parent_data["Total initial monthly pension"])/2
                                        dep_obj.eis_monthly_amount = safe_float(parent_data["Top-up monthly pension"])/2
                                        dep_obj.is_eligible = True
                                        dep_obj.save(username=self.user.username)
                            elif rel== "Widow" or rel =="Dependent widower":
                                for wife_data in vba_data:
                                    if wife_data["ID"] == "Spouse(s) and Orphan(s)":
                                        dep_obj.eis_calculated_amount = safe_float(wife_data["PV Total pension"])
                                        dep_obj.eis_approved_amount = safe_float(wife_data["PV Top-Up pension"])
                                        dep_obj.pv_factor = safe_float(wife_data["PV factor"])
                                        dep_obj.initial_replacement_rate = safe_float(wife_data["Initial replacement rate"])
                                        dep_obj.eis_initial_monthly_amount = safe_float(wife_data["Total initial monthly pension"])
                                        dep_obj.eis_monthly_amount = safe_float(wife_data["Top-up monthly pension"])
                                        dep_obj.is_eligible = True
                                        dep_obj.save(username=self.user.username)
                            else:
                                dep_obj.eis_calculated_amount = safe_float(data["PV Total pension"])
                                dep_obj.eis_approved_amount = safe_float(data["PV Top-Up pension"])
                                dep_obj.pv_factor = safe_float(data["PV factor"])
                                dep_obj.initial_replacement_rate = safe_float(data["Initial replacement rate"])
                                dep_obj.eis_initial_monthly_amount = safe_float(data["Total initial monthly pension"])
                                dep_obj.eis_monthly_amount =safe_float(data["Top-up monthly pension"])
                                dep_obj.is_eligible = True
                                dep_obj.save(username=self.user.username)
                            return True
                    return False

                relation = dependent.relation_with_worker
                marital = dependent.marital_status
                disability = dependent.disability_status

                # --- Relation-wise Eligibility ---
                if relation == "workforce.relation.brother":
                    if age < 18:
                        set_vba_data(dep_obj, "Dependent minor brother")

                elif relation == "workforce.relation.sister":
                    if age < 18:
                        set_vba_data(dep_obj, "Dependent minor sister")
                    elif marital == "workforce.marital_status.unmarried":
                        set_vba_data(dep_obj, "Dependent unmarried sister")
                    elif marital == "workforce.marital_status.widowed":
                        set_vba_data(dep_obj, "Dependent widowed sister")

                elif relation == "workforce.relation.daughter":
                    if disability == "yes":
                        set_vba_data(dep_obj, "Dependent disabled daughter")
                    elif marital == "workforce.marital_status.unmarried":
                        set_vba_data(dep_obj, "Unmarried daughter")
                    elif marital == "workforce.marital_status.widowed":
                        set_vba_data(dep_obj, "Dependent widowed daughter")
                    elif age < 18:
                        set_vba_data(dep_obj, "Minor daughter")

                elif relation == "workforce.relation.son":
                    if disability == "yes":
                        set_vba_data(dep_obj, "Dependent disabled son")
                    elif age < 18:
                        set_vba_data(dep_obj, "Minor son")

                elif relation == "workforce.relation.husband":
                    set_vba_data(dep_obj, "Dependent widower")

                elif relation == "workforce.relation.wife":
                    set_vba_data(dep_obj, "Widow")

                elif relation == "workforce.relation.father":
                    set_vba_data(dep_obj, "Dependent father")

                elif relation == "workforce.relation.mother":
                    set_vba_data(dep_obj, "Mother")

                elif relation == "workforce.relation.grand_father":
                    set_vba_data(dep_obj, "Dependent paternal grandfather")

                elif relation == "workforce.relation.grand_monther":
                    set_vba_data(dep_obj, "Dependent paternal grandmother")

                elif relation == "workforce.relation.grand_son":
                    if age < 18:
                        set_vba_data(dep_obj, "Dependent minor son of a deceased son")

                elif relation == "workforce.relation.grand_daughter":
                    if age < 18:
                        set_vba_data(dep_obj, "Dependent minor daughter of a deceased son")

                elif relation == "workforce.relation.daughter_in_law":
                    if marital == "workforce.marital_status.widowed":
                        set_vba_data(dep_obj, "Dependent widowed daughter-in-law")

                elif relation == "workforce.relation.illegitimate_son":
                    set_vba_data(dep_obj, "Dependent son born out of wedlock")

                elif relation == "workforce.relation.illegitimate_daughter":
                    if marital == "workforce.marital_status.unmarried":
                        set_vba_data(dep_obj, "Dependent unmarried daughter born out of wedlock")

                else:
                    dep_obj.is_eligible = False
                    dep_obj.save(username=self.user.username)