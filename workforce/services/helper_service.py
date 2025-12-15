import re
import uuid
import json
import random
import base64
import logging
from core.models import Role
from django.apps import apps
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError

from location.models import Location
from ..models import (
    WorkforceGrantMoney, WorkforceEisPaymentProcess, WorkforceFactory, WorkforceAssociation,
    WorkforceOrganizationEmployee, WorkforceEmployeeDependent, Bank, WorkforceEmployee, WorkforceEmployeeBankingInfo,
    WorkforceDocument
)

logger = logging.getLogger(__name__)
now = timezone.now()

WorkforceApplication = apps.get_model("workforce", "WorkforceApplication")
WorkforceApplicationMovement = apps.get_model("workforce", "WorkforceApplicationMovement")
UserRole = apps.get_model("core", "UserRole")
User = apps.get_model("core", "User")


def extract_uuid(encoded_str):
    decoded = base64.b64decode(encoded_str).decode()
    return decoded.split(":")[1]


def clean_dependents_data(dependents_data):
    """
    Filters out empty or invalid dependents from dependents_data.
    """
    if not isinstance(dependents_data, list):
        return []

    def is_valid_dependent(dep):
        return isinstance(dep, dict) and bool(dep.keys())

    return [dep for dep in dependents_data if is_valid_dependent(dep)]


def create_application_movement(
        *,
        application_id,
        status,
        action,
        role_name,
        user_str,
        note="",
        application_to=None
):
    """
    Generic application movement creator.

    Parameters
    ----------
    application_id : UUID or str
        ID of the WorkforceApplication
    status : str
        Status for the movement
    action : str
        Action for the movement
    role_name : str
        Target role name (must exist in Role)
    user_str : str
        Logged-in user string (to extract UUID)
    note : str, optional
        Movement note
    application_to : UUID or int, optional
        Target user ID (if None, will be auto-resolved from role)

    Returns
    -------
    WorkforceApplicationMovement instance
    """
    try:
        # Extract the logged-in user's UUID
        match = re.search(r"\[([0-9a-fA-F-]{36})\]", user_str)
        user_created_uuid = match.group(1) if match else None

        if not user_created_uuid:
            raise ValidationError("Cannot extract user UUID from user string.")

        user_instance = User.objects.get(id=user_created_uuid)
        core_user_obj = user_instance
        application_from = core_user_obj.i_user_id

        # Resolve role
        try:
            role_instance = Role.objects.get(name=role_name)
        except Role.DoesNotExist:
            raise ValidationError(f"Role '{role_name}' not found in core_role table.")

        # If target user not provided, try to resolve automatically based on role.from
        # Applicable for doctors and more
        if not application_to:
            user_ids = (
                UserRole.objects.filter(role=role_instance)
                .values_list("user_id", flat=True)
                .distinct()
            )
            if not user_ids:
                raise ValidationError(f"No users found for role '{role_name}'.")
            application_to = user_ids[0]

        # Create movement
        movement = WorkforceApplicationMovement(
            id=uuid.uuid4(),
            is_deleted=False,
            json_ext={},
            date_created=now,
            date_updated=now,
            note=note or "",
            action=action,
            status=status,
            application_id=uuid.UUID(str(application_id)),
            user_created=user_instance,
            user_updated=user_instance,
            application_from_id=application_from,
            application_to_id=application_to,
            to_role=role_instance,
        )
        movement.save(username=core_user_obj.username)
        logger.info(f"Movement created for application {application_id} -> {role_name}")
        return movement

    except Exception as e:
        logger.error(f"Error while creating movement for {application_id}: {e}")
        raise ValidationError(f"Failed to create movement: {str(e)}")


def get_current_year():
    return str(datetime.now().year)


def generate_random_number(digit_count: int) -> int:
    if digit_count <= 0:
        raise ValueError("digit_count must be a positive integer")

    # Smallest number with the given number of digits
    start = 10**(digit_count - 1)
    # Largest number with the given number of digits
    end = (10**digit_count) - 1

    return random.randint(start, end)


def generate_beneficiary_id(association, accident_type, application_id=None, dependent_count=None):
    while True:
        eis_payment_process_instance = WorkforceEisPaymentProcess.objects.filter(
            workforce_application_id=application_id
        ).first()
        if eis_payment_process_instance is None:
            random_number = generate_random_number(5)
        else:
            beneficiary_id_existing = eis_payment_process_instance.beneficiary_id
            random_number = beneficiary_id_existing.split(".")[-2]

        if accident_type:
            grant_money_instance = WorkforceGrantMoney.objects.filter(
                organization_type="eis",
                application_type=accident_type
            ).first()
            accident_type_no = str(grant_money_instance.application_type_no)
        else:
            accident_type_no = "00"

        # Using dummy data for association.
        # Patch this part after building association numbering mechanism.
        if association is None:
            association = "00"
        elif association == "BGMEA":
            association = "01"
        elif association == "BEPZA":
            association = "02"

        if dependent_count is None:
            beneficiary_id = f"EIS.{get_current_year()}.{association}.{accident_type_no}.{random_number}"
        else:
            beneficiary_id = f"EIS.{get_current_year()}.{association}.{accident_type_no}.{random_number}.{dependent_count}"

        # Check for duplicate
        if not WorkforceEisPaymentProcess.objects.filter(beneficiary_id=beneficiary_id).exists():
            break

    return beneficiary_id


def cf_and_eis_application_movement_to_factory_admin(self, application_instance, application_id_for_movement):
    application_to = None
    try:
        if application_instance.employee_factory_id:
            factory = WorkforceFactory.objects.filter(id=application_instance.employee_factory_id).first()
            if factory and factory.workforce_representative_id:
                representative = factory.workforce_representative
                application_to = representative.related_user_id
    except Exception as e:
        logger.error(
            f"Failed to resolve Factory Representative for Application {application_id_for_movement}: {e}")
        application_to = None

    if not application_to:
        raise ValueError(
            f"No Factory Representative (related_user_id) found for factory ID "
            f"{application_instance.employee_factory_id}"
        )
    # Create movement to Factory Admin
    create_application_movement(
        application_id=application_id_for_movement,
        status='new',
        action='forward_to_factory_admin',
        role_name='Factory Admin',
        user_str=str(self.user),
        application_to=application_to,
        note="আবেদন ফ্যাক্টরি অ্যাডমিন এর নিকট প্রেরণ করা হয়েছে"
    )


def blwf_new_application_movement_to_dife_admin(obj_data, application_instance, application_status, self):
    # ================================================================
    # 4. Handle BLWF new application movement to DIFE admin
    # ================================================================
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

    all_bank_data_unsorted = json.loads(obj_data.get("employee_bank_info", "[]")) or []

    # Check if all_bank_data_unsorted returns valid dict
    if any(all_bank_data_unsorted):
        # Sort dict objects based on accountHolderType
        # if accountHolderType is select_from_another_dependent, move to end
        all_bank_data = sorted(
            all_bank_data_unsorted,
            key=lambda x: 1 if x.get("accountHolderType") == "select_from_another_dependent" else 0
        )
    else:
        all_bank_data = False

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
                else:
                    bank_id_decoded = None

                if holder_type == "select_from_another_dependent":
                    try:
                        parent_id = extract_uuid(bank_data.get("parentDependentId", {}).get("id"))
                        parent = WorkforceEmployeeDependent.objects.get(id=parent_id)
                    except Exception as e:
                        logger.error(
                            f"Failed to get dependent's parent: {e}")
                        parent = None

                    dependent.bank = parent.bank
                    dependent.bank_account_no = parent.bank_account_no
                    dependent.bank_account_holder_name = parent.bank_account_holder_name
                    dependent.parent_dependent = parent

                else:
                    try:
                        dependent.bank = Bank.objects.get(id=bank_id_decoded)
                    except Exception as e:
                        logger.error(
                            f"Could not find dependent's bank: {e}")

                    dependent.bank_account_no = bank_data.get("accountNumber")
                    dependent.bank_account_holder_name = bank_data.get("accountHolderName")

                    if holder_type == "other":
                        dependent.account_holder_relation_with_dependent = bank_data.get(
                            "relationshipWithAccountHolder")
                        dependent.account_holder_dob = bank_data.get("otherAccountHolderDob")
                        dependent.account_holder_nid = bank_data.get("otherAccountHolderNid")

                dependent.account_holder_type = holder_type
                workforce_employee = WorkforceEmployee.objects.get(id=application_instance.workforce_employee.id)

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
                    update_banking_info.branch = dependent.bank
                    update_banking_info.nid = (dependent.nid if dependent.nid else dependent.account_holder_nid),
                    update_banking_info.date_of_birth = dependent.account_holder_dob
                    update_banking_info.status = "active"
                    update_banking_info.amount = ("1" if banking_info.amount == "0" or banking_info.amount == None else "0")  # To bypass save fails for unchanged data
                    update_banking_info.relation_with_dependent = dependent.account_holder_relation_with_dependent
                    update_banking_info.nid = dependent.account_holder_nid
                    update_banking_info.account_holder_type = holder_type
                    update_banking_info.parent_dependent = (
                        dependent.parent_dependent if dependent.parent_dependent else None)
                    update_banking_info.save(username=self.user.username)
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
                        branch=dependent.bank,
                        nid=(dependent.nid if dependent.nid else dependent.account_holder_nid),
                        date_of_birth=dependent.account_holder_dob,
                        status="active",
                        relation_with_dependent=dependent.account_holder_relation_with_dependent,
                        account_holder_type=holder_type,
                        parent_dependent=(dependent.parent_dependent if dependent.parent_dependent else None)
                    )
                    banking_info.save(username=self.user.username)
                dependent.dummy_field = ("1" if dependent.dummy_field == "0" or dependent.dummy_field == None else "0")  # To bypass save fails for unchanged data
                dependent.save(username=self.user.username)
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
                    nid=employee.nid,
                    date_of_birth=employee.birth_date,
                    status="active"
                )
                entry.save(username=self.user.username)


def handle_dependents(application_instance, application_eis_instance, dependents_data, application_id, self):
    # ================================================================
    # 2. Handle dependents
    # ================================================================
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
                # WorkforceDocument.objects.filter(workforce_dependent=dependent).delete()
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
                birth_date=dep.get("birthDate"),
                marital_status=dep.get("maritalStatus"),
                present_address=dep.get("presentAddress"),
                permanent_address=dep.get("permanentAddress"),
                present_location=present_location_instance,
                permanent_location=permanent_location_instance,
                user_created_id=self.user.id,
                user_updated_id=self.user.id,
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
                            document = WorkforceDocument.objects.get(path=item.get("file_path"),
                                                                     url=item.get("file_url"))
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
                    user_created_id=self.user.id,
                    user_updated_id=self.user.id,
                    status="active",
                    relation_with_worker=dep.get("relationType"),
                    disability_status=dep.get("isDisabled"),
                    disability_type=dep.get("disabilityType") if "disabilityType" in dep else None
                )
                dep_instance_eis.save(username=self.user.username)
    except Exception as e:
        logger.error(f"Error while updating dependents: {e}")
        raise ValidationError("Failed to update dependents.")
