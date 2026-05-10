import base64
import random
import re
import uuid
import logging
import os
from django.apps import apps
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import Role
from datetime import datetime

from ..models import WorkforceGrantMoney, WorkforceEisPaymentProcess, WorkforceFactory, WorkforceDocument, \
    WorkforceAllAssociation

logger = logging.getLogger(__name__)
now = timezone.now()

WorkforceApplication = apps.get_model("workforce", "WorkforceApplication")
WorkforceApplicationMovement = apps.get_model("workforce", "WorkforceApplicationMovement")
UserRole = apps.get_model("core", "UserRole")
User = apps.get_model("core", "User")


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

        associations= WorkforceAllAssociation.objects.all().order_by("short_name_en")
        association_position_in_db= 0
        for ass in associations:
            if ass.short_name_en== association:
                association_position_in_db += 1
                break
            else:
                association_position_in_db += 1


        # Using dummy data for association.
        # Patch this part after building association numbering mechanism.
        if association is None:
            association = "00"
        # elif association == "BGMEA":
        #     association = "01"
        # elif association == "BEPZA":
        #     association = "02"
        else:
            association = f"{association_position_in_db:02}"

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


def dependent_uuid_to_base64(uuid_str: str) -> str:
    static_prefix = "WorkforceEmployeeDependentGQLType:"
    combined = f"{static_prefix}{uuid_str}"
    encoded = base64.b64encode(combined.encode("utf-8")).decode("utf-8")
    return encoded


# helper function for generate link
def build_confirmation_link(application_id: str, base_url: str = None) -> str:
    if not application_id:
        raise ValueError("application_id is required")

    if base_url is None:
        base_url = os.environ.get("WORKFORCE_FRONTEND_URL", "http://localhost:3000")

    base_url = base_url.rstrip("/")
    return f"{base_url}/front/workforce/confirmation/{application_id}"

# def relate_document_with_banking_info(dependent_id):
#     document_instance = WorkforceDocument.objects.file()
#     pass