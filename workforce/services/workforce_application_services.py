import json
import logging
import base64
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from core.services import BaseService
from workforce.models import (
    WorkforceApplication, WorkforceGrantMoney, WorkforceEmployee, WorkforceEmployeeDependent,
    WorkforceEmployeeBankingInfo, WorkforceDocument, WorkforceFactory, Bank
)
from workforce.models import WorkforceAssociation, WorkforceOrganizationEmployee
from .helper_service import (
    create_application_movement, cf_and_eis_application_movement_to_factory_admin,
    blwf_new_application_movement_to_dife_admin, handle_dependents
)
from django.db.models import Q
from location.models import Location
from django.db import models

from .workforce_employee_dependent_services import WorkforceEmployeeDependentServices

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
                        birth_date=dep.get("birthDate"),
                        marital_status=dep.get("maritalStatus"),
                        present_address=dep.get("presentAddress"),
                        permanent_address=dep.get("permanentAddress"),
                        user_created_id=user_id,
                        user_updated_id=user_id,
                        status="active",
                        relation_with_worker= dep.get("relationType"),
                        disability_status= dep.get("isDisabled"),
                        disability_type = dep.get("disabilityType") if "disabilityType" in dep else None
                    )
                    dep_instance.save(username=self.user.username)

            except Exception as e:
                logger.error(f"Failed to save dependent: {e}")

        return application

    def update(self, obj_data):
        application_id = obj_data.get("id")
        # Fetch the complete instance before update
        try:
            application_instance_before_update = WorkforceApplication.objects.get(id=application_id)
            status_before_update = application_instance_before_update.status
        except WorkforceApplication.DoesNotExist:
            raise Exception(f"Application with id {application_id} not found")

        application = super().update(obj_data)
        application_status = obj_data.get("status")
        status = obj_data.get("status")
        user_id = self.user.id

        # Fetch the complete instance after update
        try:
            application_instance = WorkforceApplication.objects.get(id=application_id)
        except WorkforceApplication.DoesNotExist:
            raise Exception(f"Application with id {application_id} not found")

        organization_type = application_instance.organization_type
        application_type = application_instance.application_type

        # Do following steps only if status is updated.
        # Application movement only occurs when statis is updated

        # ================================================================
        # 1. Clone to EIS and create automatic movement
        # ================================================================
        if (
                organization_type == "cf"
                and application_type in ["disabilityAssistance", "financialAssistance"]
                and status == "forward_to_cf_section"
        ):
            # Build full data dict including FK IDs and JSON fields
            existing_data = {}
            for field in application_instance._meta.get_fields():
                if isinstance(field, (models.ManyToOneRel, models.ManyToManyRel)):
                    continue  # skip reverse relations

                field_name = field.name

                if field.is_relation:
                    existing_data[f"{field_name}_id"] = getattr(application_instance, f"{field_name}_id", None)
                else:
                    existing_data[field_name] = getattr(application_instance, field_name)

            # Remove primary key and other fields
            for field_name in ["id", "uuid", "validity_from", "validity_to",
                               "association_type", "grant_amount", "grant_money_id"]:
                existing_data.pop(field_name, None)

            # Override specific fields for the new clone
            existing_data["version"] = 1
            existing_data["organization_type"] = "eis"
            existing_data["status"] = "forward_to_eis_coordinator"
            existing_data["tracking_number"] = application_instance.tracking_number

            # Create new application
            application_eis = super().create(existing_data)

            # Get EIS application instance
            application_eis_id = application_eis.get("data", {}).get("id")
            application_eis_instance = WorkforceApplication.objects.get(id=application_eis_id)

            # Create automatic movement to EIS Coordinator
            create_application_movement(
                application_id=application_eis_instance.id,
                status="forward_to_eis_coordinator",
                action="forward_to_eis_coordinator",
                role_name="Eis Coordinator",
                user_str=str(self.user),
                note="আবেদন ইআইএস কোঅর্ডিনেটর শাখায় প্রেরণ করা হয়েছে"
            )

            WorkforceEmployeeDependentServices.calculate_eis_amount(application_eis_instance.id, existing_data['application_type'])
        else:
            application_eis_instance = None

        # ================================================================
        # 2. Handle dependents
        # ================================================================
        dependents_data = obj_data.get("employee_dependent_info", [])
        if dependents_data and dependents_data != "[{}]" and status == 'draft':
            handle_dependents(application_instance, application_eis_instance, dependents_data, application_id, self)

        # if status != status_before_update:
        #     # ================================================================
        #     # 3. Handle association_type + factory docs
        #     # Patch this part later as broad condition may cause documents to duplicate
        #     # ================================================================
        #     try:
        #         if application_status == "new":
        #             employee_factory_id = application_instance.employee_factory_id
        #             factory = WorkforceFactory.objects.filter(id=employee_factory_id).first()
        #             association_type = factory.association_type if factory else None
        #
        #             # Set application association type
        #             if association_type:
        #                 application_instance.association_type = association_type
        #                 application_instance.save(
        #                     username=self.user.username,
        #                     update_fields=["association_type"]
        #                 )
        #                 # Set application association type for eis application
        #                 if application_eis_instance:
        #                     application_eis_instance.association_type = association_type
        #                     application_eis_instance.save(
        #                         username=self.user.username,
        #                         update_fields=["association_type"]
        #                     )
        #
        #             # Clone factory documents only if the application has no documents yet
        #             existing_app_docs = WorkforceDocument.objects.filter(workforce_application=application_instance)
        #
        #             if not existing_app_docs.exists():
        #                 factory_documents = WorkforceDocument.objects.filter(factory_id=employee_factory_id)
        #                 if factory_documents.exists():
        #                     for doc in factory_documents:
        #                         holder_type = "dependent" if doc.workforce_dependent_id else "applicant"
        #                         new_doc = WorkforceDocument(
        #                             workforce_application=application_instance,
        #                             holder=doc.holder,
        #                             holder_type=holder_type,
        #                             verifier=doc.verifier,
        #                             approver=doc.approver,
        #                             workforce_document_type=doc.workforce_document_type,
        #                             workforce_dependent=doc.workforce_dependent,
        #                             note=doc.note,
        #                             document_type=doc.document_type,
        #                             path=doc.path,
        #                             url=doc.url,
        #                             submission_date=doc.submission_date,
        #                             verification_date=doc.verification_date,
        #                             approval_date=doc.approval_date,
        #                             remarks=doc.remarks,
        #                             status=doc.status or "active",
        #                             user_created_id=self.user.id,
        #                             user_updated_id=self.user.id,
        #                         )
        #                         new_doc.save(username=self.user.username)
        #             else:
        #                 logger.info(
        #                     f"Skipping factory document cloning for application {application_instance.id} — already has documents."
        #                 )
        #     except Exception as e:
        #         logger.error(f"Error in Step 3 (association_type/factory docs): {e}")

        # ================================================================
        # 4. Handle BLWF new application movement to DIFE admin
        # ================================================================
        if application_status == 'new' and organization_type == 'blwf' and application_status != status_before_update:
            blwf_new_application_movement_to_dife_admin(obj_data, application_instance, application_status, self)

        # ================================================================
        # 5. Handle CF and EIS new application movement to Factory Admin
        # ================================================================
        if application_status == 'new' and organization_type in ['cf', 'eis'] and application_status != status_before_update:
            application_id_for_movement = obj_data.get("id")
            application_instance = WorkforceApplication.objects.get(id=application_id_for_movement)
            cf_and_eis_application_movement_to_factory_admin(self, application_instance, application_id_for_movement)
