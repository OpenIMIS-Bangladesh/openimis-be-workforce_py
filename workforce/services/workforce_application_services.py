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
from .helper_service import create_application_movement, cf_and_eis_application_movement_to_factory_admin
from django.db.models import Q
from location.models import Location
from django.db import models

from .workforce_employee_dependent_services import WorkforceEmployeeDependentServices

logger = logging.getLogger(__name__)


def extract_uuid(encoded_str):
    decoded = base64.b64decode(encoded_str).decode()
    return decoded.split(":")[1]

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

                # Restrict to 1 application per NID for financialAssistance of CF and EIS individually
                if application_type == "financialAssistance":
                    try:
                        workforce_employee = WorkforceEmployee.objects.get(
                            id=obj_data.get("workforce_employee_id")
                        )
                        employee_nid = workforce_employee.nid

                        if organization_type == "cf":
                            existing_applications_cf = WorkforceApplication.objects.filter(
                                application_type="financialAssistance",
                                workforce_employee__nid=employee_nid,
                                organization_type="cf"
                            ).exclude(status="draft")

                            if existing_applications_cf.exists():
                                raise ValidationError(
                                    "An application for financial assistance from cf already exists for this NID."
                                )
                        if organization_type == "eis":
                            existing_applications_eis = WorkforceApplication.objects.filter(
                                application_type="financialAssistance",
                                workforce_employee__nid=employee_nid,
                                organization_type="eis"
                            ).exclude(status="draft")

                            if existing_applications_eis.exists():
                                raise ValidationError(
                                    "An application for financial assistance from eis already exists for this NID."
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
        if dependents_data and dependents_data != "[{}]":
            try:
                # Remove old dependents + related banking info for CF application
                existing_dependents = WorkforceEmployeeDependent.objects.filter(
                    workforce_application=application_instance
                )
                for dependent in existing_dependents:
                    WorkforceEmployeeBankingInfo.objects.filter(dependant=dependent).delete()
                    WorkforceDocument.objects.filter(workforce_dependent=dependent).delete()
                existing_dependents.delete()

                # Remove old dependents + related banking info for EIS (if exists)
                if application_eis_instance:
                    existing_dependents_eis = WorkforceEmployeeDependent.objects.filter(
                        workforce_application=application_eis_instance
                    )
                    for dependent in existing_dependents_eis:
                        WorkforceEmployeeBankingInfo.objects.filter(dependant=dependent).delete()
                        WorkforceDocument.objects.filter(workforce_dependent=dependent).delete()
                    existing_dependents_eis.delete()

                # Create new dependent data
                dependents = json.loads(dependents_data)
                for dep in dependents:

                    present_location_instance = Location.objects.get(
                        id=extract_uuid(dep.get("presentLocation", {}).get("id")))
                    permanent_location_instance = Location.objects.get(
                        id=extract_uuid(dep.get("permanentLocation", {}).get("id")))

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
                        birth_date= dep.get("birthDate"),
                        marital_status=dep.get("maritalStatus"),
                        present_address=dep.get("presentAddress"),
                        permanent_address=dep.get("permanentAddress"),
                        present_location=present_location_instance,
                        permanent_location=permanent_location_instance,
                        user_created_id=user_id,
                        user_updated_id=user_id,
                        status="active",
                        relation_with_worker=dep.get("relationType"),
                        disability_status=dep.get("isDisabled"),
                        disability_type=dep.get("disabilityType") if "disabilityType" in dep else None
                    )
                    dep_instance.save(username=self.user.username)

                    attachments = dep.get("attachments")
                    if attachments and attachments != "[{}]":

                        for attr in attachments:
                            files = attr.get("files", [])
                            file_data = [
                                {
                                    "file_url": info.get("uploadInfo", {}).get("file_url"),
                                    "file_path": info.get("uploadInfo", {}).get("file_path")
                                }
                                for info in files
                            ]

                            for item in file_data:
                                try:
                                    document = WorkforceDocument.objects.get(path=item.get("file_path"), url=item.get("file_url"))
                                except WorkforceDocument.DoesNotExist:
                                    continue

                                document.workforce_dependent_id = dep_instance.id
                                document.workforce_application_id = application_id
                                document.save(username=self.user.username)

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
                            birth_date=dep.get("birthDate"),
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
            application_id_for_movement = obj_data.get("id")
            employee = application_instance.workforce_employee
            present_location = employee.present_location
            applicant_location = None

            if present_location:
                location = present_location
                while location:
                    if location.type == 'D':
                        applicant_location = location.id
                        break
                    location = location.parent

            association = None
            for assoc in WorkforceAssociation.objects.filter(association_type='dife'):
                if assoc.jurisdiction_locations:
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

            # Create movement to DIFE Admin
            create_application_movement(
                application_id=application_id_for_movement,
                status='new',
                action='forward_to_dife_admin',
                role_name='blwf_dol_dife',
                user_str=str(self.user),
                application_to=application_to,
                note=""
            )

        # has_dependent_application_types = {
        #     "financialAssistance",
        #     "deadlyGrant",
        #     "medicalAssistance",
        #     "medicalDonation",
        # }

        all_bank_data_unsorted = json.loads(obj_data.get("employee_bank_info", "[]")) or []

        # Check if all_bank_data_unsorted returns valid dict
        if any(all_bank_data_unsorted):
            # Sort dict objects based on accountHolderType
            # if accountHolderType is select_from_another_dependent, move to end
            all_bank_data = sorted(
                all_bank_data_unsorted,
                key=lambda x: 1 if x.get("accountHolderType") == "select_from_another_dependent" else 0
            )

        if application_status == "new" and all_bank_data:
            # if application_instance.application_type in has_dependent_application_types:
            for bank_data in all_bank_data:
                if bank_data.get("applicant_type") == "dependent":
                    try:
                        dependent_id = extract_uuid(bank_data.get("dependentId"))
                        dependent = WorkforceEmployeeDependent.objects.get(id=dependent_id)
                    except WorkforceEmployeeDependent.DoesNotExist:
                        continue

                    holder_type = bank_data.get("accountHolderType")
                    if holder_type != "select_from_another_dependent" and holder_type != "other":
                        bank_id_decoded = extract_uuid(bank_data.get("branch", {}).get("id"))

                    if holder_type == "select_from_another_dependent":
                        try:
                            parent_id = extract_uuid(bank_data.get("parentDependentId", {}).get("id"))
                            parent = WorkforceEmployeeDependent.objects.get(id=parent_id)
                        except Exception as e:
                            logger.error(
                                f"Unknown error: {e}")

                        dependent.bank = parent.bank
                        dependent.bank_account_no = parent.bank_account_no
                        dependent.bank_account_holder_name = parent.bank_account_holder_name
                        dependent.parent_dependent = parent

                    else:
                        try:
                            dependent.bank = Bank.objects.get(id=bank_id_decoded)
                        except:
                            continue

                        dependent.bank_account_no = bank_data.get("accountNumber")
                        dependent.bank_account_holder_name = bank_data.get("accountHolderName")

                        if holder_type == "other":
                            dependent.account_holder_relation_with_dependent = bank_data.get(
                                "relationshipWithAccountHolder")
                            dependent.account_holder_dob = bank_data.get("otherAccountHolderDob")
                            dependent.account_holder_nid = bank_data.get("otherAccountHolderNid")

                    dependent.account_holder_type = holder_type
                    workforce_employee = WorkforceEmployee.objects.get(id=application_instance.workforce_employee.id)

                    banking_info= WorkforceEmployeeBankingInfo.objects.filter(dependant= dependent).first()
                    if banking_info:
                        update_banking_info= WorkforceEmployeeBankingInfo.objects.get(id=banking_info.id)
                        update_banking_info.dependant = dependent
                        update_banking_info.type = "dependent"
                        update_banking_info.employee = workforce_employee
                        update_banking_info.name_bn = dependent.name_bn
                        update_banking_info.name_en = dependent.name_en
                        update_banking_info.application = application_instance
                        update_banking_info.account_holder_name = dependent.bank_account_holder_name
                        update_banking_info.account_no = dependent.bank_account_no
                        update_banking_info.branch = dependent.bank
                        update_banking_info.nid = (dependent.nid if dependent.nid else dependent.account_holder_nid),
                        update_banking_info.date_of_birth = dependent.account_holder_dob
                        update_banking_info.status = "active"
                        update_banking_info.amount= ("1" if banking_info.amount=="0" or banking_info.amount==None else "0")
                        update_banking_info.relation_with_dependent = dependent.account_holder_relation_with_dependent
                        update_banking_info.nid = dependent.account_holder_nid
                        update_banking_info.account_holder_type = holder_type
                        update_banking_info.parent_dependent= (dependent.parent_dependent if dependent.parent_dependent else None)
                        update_banking_info.save(username=self.user.username)
                    else:
                        banking_info= WorkforceEmployeeBankingInfo(
                            dependant=dependent,
                            type="dependent",
                            employee=workforce_employee,
                            name_bn=dependent.name_bn,
                            name_en=dependent.name_en,
                            application=application_instance,
                            account_holder_name=dependent.bank_account_holder_name,
                            account_no=dependent.bank_account_no,
                            branch=dependent.bank,
                            nid=(dependent.nid if dependent.nid else dependent.account_holder_nid),
                            date_of_birth=dependent.account_holder_dob,
                            status="active",
                            relation_with_dependent=dependent.account_holder_relation_with_dependent,
                            account_holder_type= holder_type,
                            parent_dependent= (dependent.parent_dependent if dependent.parent_dependent else None)
                        )
                        banking_info.save(username=self.user.username)
                    dependent.dummy_field = ("1" if dependent.dummy_field=="0" or dependent.dummy_field==None else "0")
                    dependent.save(username=self.user.username)
                else:
                    bank_id_decoded = extract_uuid(bank_data.get("branch", {}).get("id"))
                    bank = Bank.objects.get(id=bank_id_decoded)
                    employee = WorkforceEmployee.objects.get(id= application_instance.workforce_employee.id)
                    entry = WorkforceEmployeeBankingInfo(
                        name_bn=employee.first_name_bn,
                        name_en=employee.first_name_en,
                        account_holder_name=bank_data.get("accountHolderName"),
                        employee=employee,
                        application=application_instance,
                        branch=bank,
                        type="applicant",
                        amount="0",
                        account_no=bank_data.get("accountNumber"),
                        nid=employee.nid,
                        date_of_birth=employee.birth_date,
                        status="active"
                    )
                    entry.save(username=self.user.username)

        # ================================================================
        # 5. Handle CF and EIS new application movement to Factory Admin
        # ================================================================
        if application_status == 'new' and organization_type in ['cf', 'eis'] and application_status != status_before_update:
            application_id_for_movement = obj_data.get("id")
            application_instance = WorkforceApplication.objects.get(id=application_id_for_movement)
            cf_and_eis_application_movement_to_factory_admin(self, application_instance, application_id_for_movement)
