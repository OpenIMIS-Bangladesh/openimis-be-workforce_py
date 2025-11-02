import json
import logging
import re
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from core.services import BaseService
from workforce.models import (
    WorkforceApplication, WorkforceGrantMoney, WorkforceEmployee, WorkforceEmployeeDependent,
    WorkforceEmployeeBankingInfo, WorkforceDocument, WorkforceFactory
)
from workforce.models import WorkforceAssociation, WorkforceOrganizationEmployee
from .helper_service import application_movement_to_dol_dife_admin
from django.db.models import Q
from django.apps import apps
from django.utils import timezone
from core.models import Role
import uuid

from django.db import models
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

        # # clone cf application for eis
        # if organization_type == "cf" and application_type in ["disabilityAssistance", "financialAssistance"]:
        #     # Clone obj_data for second application
        #     new_data = obj_data.copy()
        #     new_data["organization_type"] = "eis"
        #     new_data.pop("id", None)
        #
        #     # Create the second application
        #     application_eis = super().create(new_data)
        #
        #     # Get eis application instance
        #     application_eis_id = application_eis.get("data", {}).get("id")
        #     application_eis_instance = WorkforceApplication.objects.get(id=application_eis_id)
        # else:
        #     application_eis_instance = None

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
                        status="active",
                        relation_with_worker= dep.get("relationType"),
                        disability_status= dep.get("isDisabled"),
                        disability_type = dep.get("disabilityType") if "disabilityType" in dep else None
                    )
                    dep_instance.save(username=self.user.username)

                    # # Save dependents for eis application (if exists)
                    # if application_eis_instance:
                    #     dep_instance_eis = WorkforceEmployeeDependent(
                    #         workforce_application=application_eis_instance,
                    #         name_bn=dep.get("nameBn"),
                    #         name_en=dep.get("nameEn"),
                    #         father_name_bn=dep.get("fatherNameBn"),
                    #         father_name_en=dep.get("fatherNameEn"),
                    #         mother_name_bn=dep.get("motherNameBn"),
                    #         mother_name_en=dep.get("motherNameEn"),
                    #         nid=dep.get("nid"),
                    #         phone_number=dep.get("phoneNumber"),
                    #         email=dep.get("email"),
                    #         occupation=dep.get("occupation"),
                    #         birth_certificate_no=dep.get("birthCertificateNo"),
                    #         marital_status=dep.get("maritalStatus"),
                    #         present_address=dep.get("presentAddress"),
                    #         permanent_address=dep.get("permanentAddress"),
                    #         user_created_id=user_id,
                    #         user_updated_id=user_id,
                    #         status="active"
                    #     )
                    #     dep_instance_eis.save(username=self.user.username)

            except Exception as e:
                logger.error(f"Failed to save dependent: {e}")

        return application

    def update(self, obj_data):
        application = super().update(obj_data)
        application_status = obj_data.get("status")
        application_id = obj_data.get("id")
        status = obj_data.get("status")
        user_id = self.user.id

        # Fetch the complete instance after update
        try:
            application_instance = WorkforceApplication.objects.get(id=application_id)
        except WorkforceApplication.DoesNotExist:
            raise Exception(f"Application with id {application_id} not found")

        organization_type = application_instance.organization_type
        application_type = application_instance.application_type

        # Condition for cloning to EIS
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

            # Remove primary key and other non-clone fields
            existing_data.pop("id", None)
            existing_data.pop("uuid", None)
            existing_data.pop("validity_from", None)
            existing_data.pop("validity_to", None)
            existing_data.pop("association_type", None)
            existing_data.pop("grant_amount", None)
            existing_data.pop("grant_money_id", None)

            # Override specific fields for the new clone
            existing_data["version"] = 1
            existing_data["organization_type"] = "eis"
            existing_data["status"] = "forward_to_eis_coordinator"
            existing_data["tracking_number"] = application_instance.tracking_number

            # Create new application
            application_eis = super().create(existing_data)

            # Get eis application instance
            application_eis_id = application_eis.get("data", {}).get("id")
            application_eis_instance = WorkforceApplication.objects.get(id=application_eis_id)

            # Auto move eis application
            """
            ********************************************
                        Hot Fix Start
            ********************************************
            """

            WorkforceApplicationMovement = apps.get_model("workforce", "WorkforceApplicationMovement")
            UserRole = apps.get_model("core", "UserRole")
            User = apps.get_model("core", "User")

            user_str = str(self.user)
            match = re.search(r"\[([0-9a-fA-F-]{36})\]", user_str)
            user_created_uuid = match.group(1) if match else None
            core_user_obj = User.objects.get(id=user_created_uuid)
            application_from = core_user_obj.i_user_id

            action = "forward_to_eis_coordinator"
            status = "forward_to_eis_coordinator"
            role_name = "Eis Coordinator"

            # Get the Role instance
            try:
                role_instance = Role.objects.get(name=role_name)
            except Role.DoesNotExist:
                raise ValidationError(f"Role '{role_name}' not found in core_role table.")

            # Get the user(s) associated with that Role
            eis_user_ids = list(
                UserRole.objects.filter(role__name=role_name)
                .values_list("user_id", flat=True)
                .distinct()
            )

            if not eis_user_ids:
                raise ValidationError(f"No users found for role '{role_name}'.")

            # Since only one user should have this role, take the first
            eis_coordinator = eis_user_ids[0]

            # Validate the user instance
            try:
                user_instance = User.objects.get(id=user_created_uuid)
            except User.DoesNotExist:
                raise ValidationError(f"User with UUID {user_created_uuid} does not exist.")

            now = timezone.now()

            # Start from obj_data copy
            movement_data = obj_data.copy()

            # Remove known unwanted fields
            for field in ["id", "grant_money_id", "grant_amount"]:
                movement_data.pop(field, None)

            # Keep only fields that exist in WorkforceApplicationMovement
            movement_model_fields = {f.name for f in WorkforceApplicationMovement._meta.get_fields()}
            movement_data = {k: v for k, v in movement_data.items() if k in movement_model_fields}

            # Add/override with required movement fields
            movement_data.update({
                "id": uuid.uuid4(),
                "is_deleted": False,
                "json_ext": {},
                "date_created": now,
                "date_updated": now,
                "version": 1,
                "note": "আবেদন ইআইএস কোঅর্ডিনেটর শাখায় প্রেরণ করা হয়েছে",
                "action": action,
                "status": status,
                "application_id": application_eis_instance.id,
                "user_created": user_instance,
                "user_updated": user_instance,
                "application_from_id": application_from,
                "application_to_id": eis_coordinator,
                "to_role": role_instance,
            })

            # Create and save
            movement = WorkforceApplicationMovement(**movement_data)

            movement.save(username=core_user_obj.username)

            """
            ********************************************
                            Hot Fix End
            ********************************************
            """
        else:
            application_eis_instance = None

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
                        status="active",
                        relation_with_worker = dep.get("relationType"),
                        disability_status = dep.get("isDisabled"),
                        disability_type = dep.get("disabilityType") if "disabilityType" in dep else None
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
                            status="active",
                            relation_with_worker=dep.get("relationType"),
                            disability_status=dep.get("isDisabled"),
                            disability_type=dep.get("disabilityType") if "disabilityType" in dep else None
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
                        user_updated_id=self.user.id,

                    )
                    new_doc.save(username=self.user.username)

        if application_status == 'new' and organization_type == 'blwf':

            application_id_for_movement = obj_data.get("id")
            application_instance = WorkforceApplication.objects.get(id=application_id_for_movement)
            employee = application_instance.workforce_employee
            present_location = employee.present_location
            applicant_location = None

            if present_location:
                location = present_location
                while location:
                    if location.type == 'D':  # Found a 'District'-type location
                        applicant_location = location.id
                        break
                    location = location.parent

            association = None
            for assoc in WorkforceAssociation.objects.filter(association_type='dife'):
                if assoc.jurisdiction_locations:
                    # Split jurisdiction_locations string into list of IDs
                    loc_ids = [loc_id.strip() for loc_id in assoc.jurisdiction_locations.split(',')]
                    if str(applicant_location) in loc_ids:
                        association = assoc
                        break

            if not association:
                raise ValueError(f"No DIFE association found for location {applicant_location}")

            emp_obj = WorkforceOrganizationEmployee.objects.filter(association_id=association.id).first()

            if not emp_obj:
                raise ValueError(f"No WorkforceOrganizationEmployee found for association_id={association.id}")

            application_to = emp_obj.related_user_id
            user_str = str(self.user)
            status = 'new'
            action = 'forward_to_dife_admin'
            role_name = 'blwf_dol_dife'

            application_movement_to_dol_dife_admin(
                application_id_for_movement, status, action, role_name, user_str, application_to
            )

        return application