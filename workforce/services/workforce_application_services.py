import json
import logging
import base64
import os
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from core.services import BaseService
from rest_framework.response import Response
from rest_framework import status
from rx.linq.observable.blocking.first import first
from workforce.models import (
    WorkforceApplication, WorkforceGrantMoney, WorkforceEmployee, WorkforceEmployeeDependent,
    WorkforceEmployeeBankingInfo, WorkforceDocument, WorkforceFactory, Bank, WorkforceEisPaymentProcess,
    WorkforceApplicationSummary, WorkforceApplicationMovement, WorkforceDocumentMap
)
from workforce.models import WorkforceAssociation, WorkforceOrganizationEmployee
from .helper_service import create_application_movement, cf_and_eis_application_movement_to_factory_admin, dependent_uuid_to_base64
from django.db.models import Q
from location.models import Location
from django.db import models
from django.core.files.storage import default_storage

from .workforce_employee_dependent_services import WorkforceEmployeeDependentServices

logger = logging.getLogger(__name__)


def extract_uuid(encoded_str):
    decoded = base64.b64decode(encoded_str).decode()
    return decoded.split(":")[1]

def check_death_application_duplicacy(application=None, user=None):
    if application is None:
        Response({'status': 'error',
                  'message': 'Application was not found',
                  'key': 'APPLICATION_NOT_FOUND'}, status=status.HTTP_400_BAD_REQUEST)
    deceased_worker_info= json.loads(application.deceased_worker_info)
    existing_application = WorkforceApplication.objects.filter(
                                organization_type=application.organization_type,
                                application_type__in=["financialAssistance","deadlyGrant"]
                                # deceased_worker_info__nid=deceased_worker_info.get("nid")
                            ).exclude(
                                id=application.id
                            ).exclude(
                                status="draft"
                            )
    # if existing_application is not None:
    #     Response({'status': 'error',
    #               'message': f'Application for death already exists for this NID for organization {application.organization_type}',
    #               'key': 'APPLICATION ALREADY EXISTS'}, status=status.HTTP_400_BAD_REQUEST)
    #     return False
    # else:
    #     return True
    found= False
    for app_data in existing_application:
        dead_worker= json.loads(app_data.deceased_worker_info)
        if dead_worker.get("nid") == deceased_worker_info.get("nid"):
            found= True
            break
    ekhane_thambe= found
    if found:
        raise ValidationError(
            "An application for financial assistance from cf already exists for this NID."
        )
        # Response({'status': 'error',
        #           'message': f'Application for death already exists for this NID for organization {application.get("organization_type")}',
        #           'key': 'APPLICATION ALREADY EXISTS'}, status=status.HTTP_400_BAD_REQUEST)



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
                if application_type in ["financialAssistance","deadlyGrant"]:
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
                                Response({'status': 'error', 'message': 'An application for financial assistance from Central Fund already exists for this NID.',
                                          'key': 'INVALID_PHONE_NUMBER'}, status=status.HTTP_400_BAD_REQUEST)
                                # raise ValidationError(
                                #     "An application for financial assistance from cf already exists for this NID."
                                # )
                        if organization_type == "eis":
                            existing_applications_eis = WorkforceApplication.objects.filter(
                                application_type="financialAssistance",
                                workforce_employee__nid=employee_nid,
                                organization_type="eis"
                            ).exclude(status="draft")

                            if existing_applications_eis.exists():
                                Response({'status': 'error',
                                          'message': 'An application for financial assistance from EIS already exists for this NID.',
                                          'key': 'INVALID_PHONE_NUMBER'}, status=status.HTTP_400_BAD_REQUEST)
                                # raise ValidationError(
                                #     "An application for financial assistance from eis already exists for this NID."
                                # )

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
        try:
            application = super().create(obj_data)
        except Exception as e:
            raise Exception(f"Failed to create application because of Exception: {e}")

        application_id = application.get("data", {}).get("id")
        application_instance = WorkforceApplication.objects.get(id=application_id)

        user_id = self.user.id
        if "employee_dependent_info" in obj_data:
            dependents_data = obj_data.get("employee_dependent_info")

            # if dependents_data and application_instance.application_type=="financialAssistance":
            if dependents_data and application_instance.application_type in ["financialAssistance", "deadlyGrant","medicalAssistance", "medicalDonation"]:
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
                            relation_with_worker=dep.get("relationType") if "relationType" in dep else dep.get("relationWithWorker", None),
                            disability_status=dep.get("isDisabled"),
                            disability_type=dep.get("disabilityType") if "disabilityType" in dep else None
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

        try:
            application = super().update(obj_data)
        except Exception as e:
            raise Exception(f"Failed to update application because of Exception: {e}")

        application_status = obj_data.get("status")
        status = obj_data.get("status")
        user_id = self.user.id

        #try updating dependent info if super().update(obj_data) fails to update it
        # try:
        #     application_to_update= WorkforceApplication.objects.get(id=application_id)
        #     if application_to_update.application_type=="financialAssistance":
        #         application_to_update.employee_dependent_info= obj_data.get("employee_dependent_info")
        #         application_to_update.save()
        # except Exception as e:
        #     raise Exception(f"Failed to update application because of Exception: {e}")

        # Fetch the complete instance after update
        try:
            application_instance = WorkforceApplication.objects.get(id=application_id)
            # if application_instance.application_type in ["financialAssistance", "deadlyGrant"]:
            #     check_death_application_duplicacy(application_instance, self.user)
            if application_instance.status in ["verified", "forward_to_eis_advisor", "approved_by_eis_advisor", "forward_to_comiitee", "approved_by_committee"]:
                application_instance.eis_verified = True
            else:
                application_instance.eis_verified = False
            try:
                application_instance.save(username=self.user.username)
            except Exception as e:
                print(f"Failed to update eis verified status: {e}")

        except WorkforceApplication.DoesNotExist:
            raise Exception(f"Application with id {application_id} not found")

        try:
            if status in ["approved_by_committee"]:
                committee_forwarded_summary_applications= WorkforceApplication.objects.filter(eis_application_summary_id=application_instance_before_update.eis_application_summary_id, status="forward_to_comiittee")
                application_count= len(committee_forwarded_summary_applications)
                if application_count <1:
                    summary_instance= WorkforceApplicationSummary.objects.get(id= application_instance_before_update.eis_application_summary_id)
                    summary_instance.status = "approved_by_committee"
                    summary_instance.save(username=self.user.username)
        except Exception as e:
            print(f"Failed to update eis summary approval status: {e}")


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

        else:
            application_eis_instance = None


        #====update accident date =====#

        employee_accident_info_json=  obj_data.get("employee_accident_info", None)
        if employee_accident_info_json:
            employee_accident_info = json.loads(employee_accident_info_json, strict=False)
            accident_date= employee_accident_info.get("accidentDate", None)
            try:
                workforce_application_instance= WorkforceApplication.objects.get(id= application_instance.id)
                workforce_application_instance.accident_date= accident_date
                workforce_application_instance.save(username=self.user.username)
            except Exception as e:
                print(e)

        # ================================================================
        # 2. Handle dependents
        # ================================================================

        # if dependents_data and dependents_data != "[{}]":
        dependent_update_request = obj_data.get("employee_dependent_info", [])
        # if dependent_update_request and application_instance.application_type=="financialAssistance":
        if dependent_update_request and application_instance.application_type in ["financialAssistance", "deadlyGrant","medicalAssistance","medicalDonation"]:
            try:
                if application_status == "draft" or application_status == "new":
                    WorkforceDocumentMap.objects.filter(workforce_application_id=application_instance.id).delete()
                    WorkforceDocument.objects.filter(workforce_application_id=application_instance.id, workforce_document_type__form_step_no="employeeDependentInfo").update(workforce_dependent=None)
                    WorkforceDocument.objects.filter(workforce_application_id=application_instance.id, workforce_document_type__form_step_no="employeeBankInfo").update(workforce_employee_banking_info=None)
                    WorkforceEmployeeBankingInfo.objects.filter(application_id=application_instance.id).delete()
                    WorkforceEmployeeDependent.objects.filter(workforce_application_id=application_instance.id).delete()
                    dependents_data = obj_data.get("employee_dependent_info", [])
                    dependents = json.loads(dependents_data)
                else:
                    # get the originally updated json because tazwer always updates this
                    dependents_data = obj_data.get("employee_dependent_info") or WorkforceApplication.objects.get(
                        id=application_id).employee_dependent_info
                    dependents = json.loads(dependents_data)

                # if dependents_data and application_instance.application_type=="financialAssistance":
                if dependents_data and application_instance.application_type in ["financialAssistance","deadlyGrant", "medicalAssistance","medicalDonation"]:
                    incoming_ids = []
                    if application_status not in  ["new", "draft"]:
                        for dep in dependents:
                            dep_id = dep.get("id")
                            if dep_id:
                                incoming_ids.append(extract_uuid(dep_id))
                        try:
                            # WorkforceDocument.objects.filter(workforce_application=application_instance, workforce_dependent_id__isnull=False).exclude(workforce_dependent_id__in=incoming_ids).delete()
                            WorkforceDocumentMap.objects.filter(
                                workforce_application_id=application_instance.id).delete()
                            WorkforceDocument.objects.filter(workforce_application_id=application_instance.id,
                                                             workforce_document_type__form_step_no="employeeDependentInfo").update(
                                workforce_dependent=None)
                            WorkforceDocument.objects.filter(workforce_application_id=application_instance.id,
                                                             workforce_document_type__form_step_no="employeeBankInfo").update(
                                workforce_employee_banking_info=None)
                            WorkforceEisPaymentProcess.objects.filter(workforce_application=application_instance).exclude(workforce_employee_dependent_id__in=incoming_ids).delete()
                            WorkforceEmployeeBankingInfo.objects.filter(application=application_instance).exclude(dependant_id__in=incoming_ids).delete()
                            WorkforceEmployeeDependent.objects.filter(workforce_application=application_instance).exclude(id__in=incoming_ids).delete()
                        except Exception as e:
                            print(e)
                    for dep in dependents:
                        dependent_id= dep.get("id")
                        if dependent_id is not None:
                            dep_instance= WorkforceEmployeeDependent.objects.filter(id=extract_uuid(dep.get("id"))).first()
                        else: dep_instance = None
                        eligibility_status = dep.get("isEligible", True)
                        remarks = dep.get("remarks", None)
                        present_location_instance = Location.objects.get(
                            id=extract_uuid(dep.get("presentLocation", {}).get("id")))
                        permanent_location_instance = Location.objects.get(
                            id=extract_uuid(dep.get("permanentLocation", {}).get("id")))
                        attachments = dep.get("attachments") if "attachments" in dep.keys() else None

                        if dep_instance is not None:
                            dep_instance.workforce_application = application_instance
                            dep_instance.name_bn = dep.get("nameBn")
                            dep_instance.name_en = dep.get("nameEn")
                            dep_instance.father_name_bn = dep.get("fatherNameBn")
                            dep_instance.father_name_en = dep.get("fatherNameEn")
                            dep_instance.mother_name_bn = dep.get("motherNameBn")
                            dep_instance.mother_name_en = dep.get("motherNameEn")
                            dep_instance.nid = dep.get("nid")
                            dep_instance.phone_number = dep.get("phoneNumber")
                            dep_instance.email = dep.get("email")
                            dep_instance.occupation = dep.get("occupation")
                            dep_instance.birth_certificate_no = dep.get("birthCertificateNo")
                            dep_instance.birth_date = dep.get("birthDate")
                            dep_instance.marital_status = dep.get("maritalStatus")
                            dep_instance.present_address = dep.get("presentAddress")
                            dep_instance.permanent_address = dep.get("permanentAddress")
                            dep_instance.present_location = present_location_instance
                            dep_instance.permanent_location = permanent_location_instance
                            dep_instance.user_created_id = user_id
                            dep_instance.user_updated_id = user_id
                            dep_instance.status = "active"
                            dep_instance.attachments = attachments
                            dep_instance.relation_with_worker = dep.get("relationType") if "relationType" in dep else dep.get("relationWithWorker", None)
                            dep_instance.disability_status = dep.get("isDisabled")
                            dep_instance.percentage_of_cf_grant = dep.get("percentage_of_grant", None)
                            dep_instance.disability_type = dep.get(
                                "disabilityType") if "disabilityType" in dep else None
                            dep_instance.is_eligible = eligibility_status
                            dep_instance.remarks = remarks
                            dep_instance.dummy_field = "1" if dep_instance.dummy_field == "0" or dep_instance.dummy_field is None else "0"
                            try:
                                dep_instance.save(user=self.user)
                            except Exception as e:
                                continue
                        else:
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
                                present_location=present_location_instance,
                                permanent_location=permanent_location_instance,
                                percentage_of_cf_grant= dep.get("percentage_of_grant", None),
                                user_created_id=user_id,
                                user_updated_id=user_id,
                                status="active",
                                attachments=attachments,
                                relation_with_worker=dep.get("relationType") if "relationType" in dep else dep.get("relationWithWorker", None),
                                disability_status=dep.get("isDisabled"),
                                disability_type=dep.get("disabilityType") if "disabilityType" in dep else None,
                                is_eligible=eligibility_status,
                                remarks = remarks
                            )
                            dep_instance.save(username=self.user.username)
                        try:
                            if attachments is not None and attachments != "[{}]":

                                for attr in attachments:
                                    files = attr.get("files", [])
                                    document_type = attr.get("documentType", "")
                                    file_data = [
                                        {
                                            "file_url": info.get("url"),
                                            "file_path": info.get("path"),
                                            "document_type": document_type
                                        }
                                        for info in files
                                    ]

                                    for item in file_data:
                                        try:
                                            document = WorkforceDocument.objects.filter(
                                                path=item.get("file_path")).first()
                                            if not document:
                                                document = WorkforceDocument(
                                                    path=item.get("file_path"),
                                                    url=item.get("file_url"),
                                                    workforce_application_id=application_id,
                                                    document_type=item.get("document_type")
                                                )
                                            document.workforce_dependent_id = dep_instance.id
                                            document.save(username=self.user.username)
                                        except Exception as e:
                                            logger.error(f"Document save error: {e}")
                                            continue
                        except Exception as e:
                            continue


            except Exception as e:
                logger.error(f"Error while updating dependents: {e}")
                # raise ValidationError("Failed to update dependents.")


        #######################################################################
        ##################### Set dependents or applicant bank data ########################
        #######################################################################

        all_bank_data_unsorted = json.loads(obj_data.get("employee_bank_info", "[]")) or []
        # all_bank_data_unsorted = json.loads(WorkforceApplication.objects.get(id=application_id).employee_bank_info) or []

        # Check if all_bank_data_unsorted returns valid dict
        if any(all_bank_data_unsorted):
            # Sort dict objects based on accountHolderType
            # if accountHolderType is select_from_another_dependent, move to end
            all_bank_data = sorted(
                all_bank_data_unsorted,
                key=lambda x: 1 if x.get("accountHolderType") == "select_from_another_dependent" else 0
            )

            valid_status = {
                "new",
                "verified",
                "forward_for_verification",
                "approved_by_doctor",
                "revert"
            }
            if (
                all_bank_data
                and (
                    application_status in valid_status
                    or application_instance.status in valid_status
                )
            ):
                # if application_instance.application_type in has_dependent_application_types:
                # if len(incoming_ids)>0 and application_status not in  ["new", "draft"]:
                #     WorkforceEmployeeBankingInfo.objects.filter(application= application_instance).exclude(dependent_id__in=incoming_ids).delete()
                for bank_data in all_bank_data:
                    bank_info_id= None;
                    if bank_data.get("applicant_type") == "dependent":
                        try:
                            # dependent_id_decoded= extract_uuid(bank_data.get("dependentId"))
                            dependent_nid= bank_data.get("dependentNid")
                            # dependent = WorkforceEmployeeDependent.objects.get(id=dependent_id_decoded)
                            dependent = WorkforceEmployeeDependent.objects.filter(workforce_application=application_instance, nid=dependent_nid).first()
                        except WorkforceEmployeeDependent.DoesNotExist:
                            continue

                        holder_type = bank_data.get("accountHolderType")
                        if holder_type != "select_from_another_dependent" and holder_type != "other":
                            bank_id_decoded = extract_uuid(bank_data.get("branch", {}).get("id"))

                        if holder_type == "select_from_another_dependent":
                            try:
                                parent_id = bank_data.get("parentDependentId", {}).get("id")
                                parent_nid= None
                                for parent_data in all_bank_data:
                                    if parent_data.get("dependentId") == parent_id:
                                        parent_nid= parent_data.get("dependentNid")
                                parent = WorkforceEmployeeDependent.objects.filter(workforce_application=application_instance, nid=parent_nid).first()
                            except Exception as e:
                                logger.error(
                                    f"Unknown error: {e}")

                            try:
                                dependent.bank = parent.bank
                                dependent.bank_account_no = parent.bank_account_no
                                dependent.routing_number = parent.routing_number
                                dependent.bank_account_holder_name = parent.bank_account_holder_name
                                dependent.parent_dependent = parent
                            except Exception as e:
                                continue

                        else:
                            try:
                                dependent.bank = Bank.objects.get(id=bank_id_decoded)
                            except:
                                continue

                            dependent.bank_account_no = bank_data.get("accountNumber")
                            dependent.routing_number = bank_data.get("routingNumber", None)
                            dependent.bank_account_holder_name = bank_data.get("accountHolderName")

                            if holder_type == "other":
                                dependent.account_holder_relation_with_dependent = bank_data.get(
                                    "relationshipWithAccountHolder")
                                dependent.account_holder_dob = bank_data.get("otherAccountHolderDob")
                                dependent.account_holder_nid = bank_data.get("otherAccountHolderNid")

                        dependent.account_holder_type = holder_type
                        workforce_employee = WorkforceEmployee.objects.get(
                            id=application_instance.workforce_employee.id)

                        banking_info = WorkforceEmployeeBankingInfo.objects.filter(dependant=dependent).first()
                        if banking_info:
                            update_banking_info = WorkforceEmployeeBankingInfo.objects.get(id=banking_info.id)
                            update_banking_info.dependant = dependent
                            update_banking_info.type = "dependent"
                            update_banking_info.employee = workforce_employee
                            update_banking_info.name_bn = dependent.name_bn
                            update_banking_info.name_en = dependent.name_en
                            update_banking_info.application = application_instance
                            update_banking_info.account_holder_name = dependent.bank_account_holder_name
                            update_banking_info.account_no = dependent.bank_account_no
                            update_banking_info.routing_number = dependent.routing_number
                            update_banking_info.branch = dependent.bank
                            update_banking_info.nid = dependent.nid if dependent.nid else dependent.account_holder_nid,
                            update_banking_info.date_of_birth = dependent.account_holder_dob
                            update_banking_info.status = "active"
                            update_banking_info.amount = "1" if banking_info.amount == "0" or banking_info.amount == None else "0"
                            update_banking_info.relation_with_dependent = dependent.account_holder_relation_with_dependent
                            update_banking_info.nid = dependent.account_holder_nid
                            update_banking_info.account_holder_type = holder_type
                            update_banking_info.parent_dependent = dependent.parent_dependent if dependent.parent_dependent else None
                            try:
                                update_banking_info.save(username=self.user.username)
                                bank_info_id= update_banking_info.id
                            except Exception as e:
                                continue

                        else:
                            banking_info = WorkforceEmployeeBankingInfo(
                                dependant=dependent,
                                type="dependent",
                                employee=workforce_employee,
                                name_bn=dependent.name_bn,
                                name_en=dependent.name_en,
                                application=application_instance,
                                account_holder_name=dependent.bank_account_holder_name,
                                account_no=dependent.bank_account_no,
                                routing_number=dependent.routing_number,
                                branch=dependent.bank,
                                nid=dependent.nid if dependent.nid else dependent.account_holder_nid,
                                date_of_birth=dependent.account_holder_dob,
                                status="active",
                                relation_with_dependent=dependent.account_holder_relation_with_dependent,
                                account_holder_type=holder_type,
                                parent_dependent=dependent.parent_dependent if dependent.parent_dependent else None
                            )
                            banking_info.save(username=self.user.username)
                            bank_info_id= banking_info.id
                        # dependent.dummy_field =
                        #     "1" if dependent.dummy_field == "0" or dependent.dummy_field is None else "0"
                        try:
                            dependent.save(username=self.user.username)
                            attachments = bank_data.get("attachments", [])
                            if attachments and attachments != "[{}]":
                                for attr in attachments:
                                    files = attr.get("files", [])
                                    document_type = attr.get("documentType", "")  # Extract from parent object
                                    file_data = [
                                        {
                                            "file_url": info.get("url"),
                                            "file_path": info.get("path"),
                                            "document_type": document_type
                                        }
                                        for info in files
                                    ]
                                    for item in file_data:
                                        try:
                                            document = WorkforceDocument.objects.filter(path=item.get("file_path"),
                                                                                            url=item.get(
                                                                                                "file_url")).first()
                                        except WorkforceDocument.DoesNotExist:
                                            continue
                                        try:
                                            document.workforce_employee_banking_info_id = bank_info_id
                                            document.workforce_application_id = application_id
                                            document.save(username=self.user.username)
                                        except Exception as e:
                                            continue

                        except Exception as e:
                            continue
                    else:
                        bank_id_decoded = extract_uuid(bank_data.get("branch", {}).get("id"))
                        bank = Bank.objects.get(id=bank_id_decoded)
                        employee = WorkforceEmployee.objects.get(id=application_instance.workforce_employee.id)
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
                            routing_number= bank_data.get("routingNumber", None),
                            nid=employee.nid,
                            date_of_birth=employee.birth_date,
                            status="active"
                        )
                        entry.save(username=self.user.username)
                        bank_info_id= entry.id
                        attachments = bank_data.get("attachments", [])
                        if attachments and attachments != "[{}]":
                            for attr in attachments:
                                files = attr.get("files", [])
                                document_type = attr.get("documentType", "")  # Extract from parent object
                                file_data = [
                                    {
                                        "file_url": info.get("url"),
                                        "file_path": info.get("path"),
                                        "document_type": document_type
                                    }
                                    for info in files
                                ]
                                for item in file_data:
                                    try:
                                        document = WorkforceDocument.objects.filter(path=item.get("file_path"),url=item.get("file_url")).first()
                                    except WorkforceDocument.DoesNotExist:
                                        continue
                                    try:
                                        document.workforce_employee_banking_info_id = bank_info_id
                                        document.workforce_application_id = application_id
                                        document.save(username=self.user.username)
                                    except Exception as e:
                                        continue

        #clean up document table where dependent and bank id is null
        try:
            WorkforceDocument.objects.filter(workforce_application=application_instance,
                                             workforce_document_type__form_step_no="employeeDependentInfo",
                                             workforce_dependent_id__isnull=True).delete()
            WorkforceDocument.objects.filter(workforce_application=application_instance,
                                             workforce_document_type__form_step_no="employeeBankInfo",
                                             workforce_employee_banking_info_id__isnull=True).delete()
        except Exception as e:
            print(e)

        # try:
        #     documents= WorkforceDocument.objects.filter(workforce_application=application_instance, is_deleted=False)
        #     for document in documents:
        #         # --- NEW BIOMETRIC INTEGRATION ---
        #         # Ensure we only process photos linked to the dependent
        #         PHOTO_TYPES = {
        #             "nominee's photo",
        #             "nominee photo",
        #             "employee photo",
        #             "workers photo",
        #             "photo of worker",
        #         }
        #         if document.document_type in PHOTO_TYPES and document.path:
        #             try:
        #                 path = document.path
        #                 if 'file_storage' in path:
        #                     filename = path.replace("/file_storage/content/workforce/", "")
        #                 else:
        #                     filename = path.replace("/content/workforce/", "")
        #                 file_path = os.path.join('content', 'workforce', filename)
        #                 if not default_storage.exists(file_path):
        #                     continue
        #                 file = default_storage.open(file_path)
        #                 image_bytes = file.read()
        #                 # Add this with your other imports at the top
        #                 from biometric_verification.services import BiometricService
        #                 # Use the new method that accepts raw bytes and document id
        #                 result = BiometricService.compute_embedding_from_bytes(
        #                     document_id=document.id,
        #                     image_bytes=image_bytes
        #                 )
        #                 if result.success:
        #                     logger.info(
        #                         f"Generated biometric embedding for dependent {document.id}")
        #                 else:
        #                     logger.error(
        #                         f"Failed to generate embedding for dependent {document.id}: {result.error}")
        #             except Exception as e:
        #                 logger.error(
        #                     f"Failed to generate embedding for dependent {document.id}: {e}")
        #         # ---------------------------------
        # except Exception as e:
        #     print(e)

        # ================================================================
        # 4. Handle BLWF new application movement to DIFE admin
        # ================================================================
        # movement_instance= WorkforceApplicationMovement.objects.filter(application_id= application_instance.id, status="new")
        if obj_data.get("status") == 'new' and obj_data.get("organization_type") == 'blwf':
            application_id_for_movement = obj_data.get("id")
            application_type= application_instance.application_type
            if application_type == "deadlyGrant":
                employee= json.loads(application_instance.deceased_worker_info) if application_instance.deceased_worker_info else None
            else:
                employee = application_instance.workforce_employee
            present_location = employee.present_location if application_type!='deadlyGrant' else employee.get("permanentLocation")
            applicant_location = None

            try:
                if present_location:
                    location = present_location
                    while location:
                        if application_type == "deadlyGrant":
                            if location.get("type") == 'D':
                                applicant_location = extract_uuid(location.get("id"))
                                break
                            location = location.get("parent", None)
                        else:
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
            except Exception as e:
                print(e)



        # ================================================================
        # 5. Handle CF and EIS new application movement to Factory Admin
        # ================================================================
        if application_status == 'new' and organization_type in ['cf','eis'] and application_status != status_before_update:
            application_id_for_movement = obj_data.get("id")
            application_instance = WorkforceApplication.objects.get(id=application_id_for_movement)
            cf_and_eis_application_movement_to_factory_admin(self, application_instance, application_id_for_movement)
