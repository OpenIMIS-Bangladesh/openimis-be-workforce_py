import json
import logging
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from core.services import BaseService
from workforce.models import WorkforceApplication, WorkforceGrantMoney, WorkforceEmployee, WorkforceEmployeeDependent
from django.db.models import Q

logger = logging.getLogger(__name__)


class WorkforceApplicationServices(BaseService):
    OBJECT_TYPE = WorkforceApplication

    def get(self, **kwargs):
        filters = []
        model = self.OBJECT_TYPE

        client_mutation_id = kwargs.get("client_mutation_id", None)
        if client_mutation_id:
            filters.append(Q(json_ext__contains={"client_mutation_id": client_mutation_id}))

        query = model.objects.filter(*filters, is_deleted=False).all()
        return query

    def create(self, obj_data):
        application_type = obj_data.get("application_type")
        organization_type = obj_data.get("organization_type")

        if application_type and organization_type:
            try:
                grant = WorkforceGrantMoney.objects.get(
                    application_type=application_type,
                    organization_type=organization_type
                )

                obj_data["grant_money_id"] = grant.id
                obj_data["grant_amount"] = grant.grant_money

                # Tracking number generation
                year_suffix = str(datetime.now().year)[-2:]
                application_type_no = str(grant.application_type_no).zfill(2)
                existing_count = WorkforceApplication.objects.count()
                application_count_str = str(existing_count + 1).zfill(6)
                tracking_number = f"{year_suffix}{application_type_no}{application_count_str}"
                obj_data["tracking_number"] = tracking_number

                # Restrict to 1 application per NID for disabilityAssistance
                if application_type == "disabilityAssistance":
                    try:
                        workforce_employee = WorkforceEmployee.objects.get(
                            id=obj_data.get("workforce_employee_id")
                        )
                        employee_nid = workforce_employee.nid

                        existing_applications = WorkforceApplication.objects.filter(
                            application_type="disabilityAssistance",
                            workforce_employee__nid=employee_nid
                        )

                        if existing_applications.exists():
                            raise ValidationError(
                                "An application for disability assistance already exists for this NID."
                            )

                    except ObjectDoesNotExist:
                        logger.warning("No matching WorkforceEmployee found for given ID.")
                        raise ValidationError("Invalid employee ID provided.")

            except ObjectDoesNotExist:
                logger.warning(
                    "No matching WorkforceGrantMoney found for given application_type and organization_type.")
            except MultipleObjectsReturned:
                logger.error("Multiple WorkforceGrantMoney entries found. Expected only one.")
                raise

        # Save dependents data to workforce_employee_dependent table
        application = super().create(obj_data)
        application_id = application.get("data", {}).get("id")
        application_instance = WorkforceApplication.objects.get(id=application_id)
        user_id = self.user.id
        dependents_data = obj_data.get("employee_dependent_info")

        if dependents_data:
            try:
                dependents = json.loads(dependents_data)
                for dep in dependents:
                    dep_instance = WorkforceEmployeeDependent(
                        workforce_application=application_instance,
                        name_bn=dep.get("nameBn"),
                        name_en=dep.get("nameEn"),
                        father_name_bn=dep.get("fatherNameBn"),
                        father_name_en=dep.get("fatherNameEn"),
                        mother_name_bn=dep.get("motherNameBn"),
                        mother_name_en=dep.get("motherNameEn"),
                        nid=dep.get("nid"),
                        phone_number=dep.get("phoneNumber"),
                        email=dep.get("email"),
                        occupation=dep.get("occupation"),
                        birth_certificate_no=dep.get("birthCertificateNo"),
                        marital_status=dep.get("maritalStatus"),
                        present_address=dep.get("presentAddress"),
                        permanent_address=dep.get("permanentAddress"),
                        user_created_id=user_id,
                        user_updated_id=user_id,
                        status="active"
                    )
                    dep_instance.save(username=self.user.username)

            except Exception as e:
                logger.error(f"Failed to save dependent: {e}")

        return application

    def update(self, obj_data):
        return super().update(obj_data)
