import json
import logging
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from core.services import BaseService
from workforce.models import (
    WorkforceApplication, WorkforceGrantMoney, WorkforceEmployee, WorkforceEmployeeDependent,
    WorkforceEmployeeBankingInfo, WorkforceDocument, WorkforceFactory
)
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

                # Restrict to 1 application per NID for financialAssistance
                if application_type == "financialAssistance":
                    try:
                        workforce_employee = WorkforceEmployee.objects.get(
                            id=obj_data.get("workforce_employee_id")
                        )
                        employee_nid = workforce_employee.nid

                        existing_applications = WorkforceApplication.objects.filter(
                            application_type="financialAssistance",
                            workforce_employee__nid=employee_nid
                        ).exclude(status="draft")

                        if existing_applications.exists():
                            raise ValidationError(
                                "An application for financial assistance already exists for this NID."
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

        if organization_type == "cf" and application_type in ["disabilityAssistance", "financialAssistance"]:
            # Clone obj_data for second application
            new_data = obj_data.copy()
            new_data["organization_type"] = "eis"
            new_data.pop("id", None)

            # Create the second application
            application_eis = super().create(new_data)

            # Get eis application instance
            application_eis_id = application_eis.get("data", {}).get("id")
            application_eis_instance = WorkforceApplication.objects.get(id=application_eis_id)
        else:
            application_eis_instance = None

        application_id = application.get("data", {}).get("id")
        application_instance = WorkforceApplication.objects.get(id=application_id)

        user_id = self.user.id
        dependents_data = obj_data.get("employee_dependent_info")

        if dependents_data and dependents_data != "[{}]":
            try:
                dependents = json.loads(dependents_data)
                for dep in dependents:
                    # Save for main application
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

                    # Save for eis application (if exists)
                    if application_eis_instance:
                        dep_instance_eis = WorkforceEmployeeDependent(
                            workforce_application=application_eis_instance,
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
                        dep_instance_eis.save(username=self.user.username)

            except Exception as e:
                logger.error(f"Failed to save dependent: {e}")

        return application

    def update(self, obj_data):
        application = super().update(obj_data)

        application_id = obj_data.get("id")
        application_status = obj_data.get("status", [])
        application_type = obj_data.get("application_type")
        organization_type = obj_data.get("organization_type")
        user_id = self.user.id

        try:
            application_instance = WorkforceApplication.objects.get(id=application_id)
        except WorkforceApplication.DoesNotExist:
            raise ValidationError("Invalid application ID provided.")

        # update eis application
        application_eis_instance = None
        if organization_type == "cf" and application_type in ["disabilityAssistance", "financialAssistance"]:
            application_eis_instance = WorkforceApplication.objects.filter(
                tracking_number=application_instance.tracking_number,
                organization_type="eis"
            ).first()

            new_data = obj_data.copy()
            new_data["organization_type"] = "eis"
            new_data["id"] = application_eis_instance.id if application_eis_instance else None

            if application_eis_instance:
                # Update eis data
                application_eis = super().update(new_data)
                application_eis_id = application_eis.get("data", {}).get("id")
                application_eis_instance = WorkforceApplication.objects.get(id=application_eis_id)
            else:
                raise ValidationError(
                    "EIS application not found for this CF application."
                )

        # Handle dependents
        dependents_data = obj_data.get("employee_dependent_info", [])

        if dependents_data and dependents_data != "[{}]":
            try:
                # Remove old dependents + related banking info for CF application
                existing_dependents = WorkforceEmployeeDependent.objects.filter(
                    workforce_application=application_instance
                )
                for dependent in existing_dependents:
                    WorkforceEmployeeBankingInfo.objects.filter(
                        dependant=dependent
                    ).delete()
                existing_dependents.delete()

                # Remove old dependents + related banking info for EIS application (if exists)
                if application_eis_instance:
                    existing_dependents_eis = WorkforceEmployeeDependent.objects.filter(
                        workforce_application=application_eis_instance
                    )
                    for dependent in existing_dependents_eis:
                        WorkforceEmployeeBankingInfo.objects.filter(
                            dependant=dependent
                        ).delete()
                    existing_dependents_eis.delete()

                # create dependent data
                dependents = json.loads(dependents_data)
                for dep in dependents:
                    # CF application
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

                    # EIS application
                    if application_eis_instance:
                        dep_instance_eis = WorkforceEmployeeDependent(
                            workforce_application=application_eis_instance,
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
                        dep_instance_eis.save(username=self.user.username)

            except Exception as e:
                logger.error(f"Error while updating dependents: {e}")
                raise ValidationError("Failed to update dependents.")

        # Handle association_type + factory docs
        if application_status == "new":
            employee_factory_id = application_instance.employee_factory_id

            factory = WorkforceFactory.objects.filter(id=employee_factory_id).first()
            association_type = factory.association_type if factory else None

            if association_type:
                application_instance.association_type = association_type
                application_instance.save(
                    username=self.user.username,
                    update_fields=["association_type"]
                )
            if application_eis_instance:
                application_eis_instance.association_type = association_type
                application_eis_instance.save(
                    username=self.user.username,
                    update_fields=["association_type"]
                )

            if employee_factory_id:
                factory_documents = WorkforceDocument.objects.filter(
                    factory_id=employee_factory_id
                )
                for doc in factory_documents:
                    holder_type = "dependent" if doc.workforce_dependent_id else "applicant"

                    new_doc = WorkforceDocument(
                        workforce_application=application_instance,
                        holder=doc.holder,
                        holder_type=holder_type,
                        verifier=doc.verifier,
                        approver=doc.approver,
                        workforce_document_type=doc.workforce_document_type,
                        workforce_dependent=doc.workforce_dependent,
                        note=doc.note,
                        document_type=doc.document_type,
                        path=doc.path,
                        url=doc.url,
                        submission_date=doc.submission_date,
                        verification_date=doc.verification_date,
                        approval_date=doc.approval_date,
                        remarks=doc.remarks,
                        status=doc.status or "active",
                        user_created_id=self.user.id,
                        user_updated_id=self.user.id
                    )
                    new_doc.save(username=self.user.username)

        return application