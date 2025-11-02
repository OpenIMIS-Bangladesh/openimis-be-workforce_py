import re
import uuid
import logging
from django.apps import apps
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from core.models import Role
from core.services import BaseService

now = timezone.now()

WorkforceApplication = apps.get_model("workforce", "WorkforceApplication")
WorkforceApplicationMovement = apps.get_model("workforce", "WorkforceApplicationMovement")
UserRole = apps.get_model("core", "UserRole")
User = apps.get_model("core", "User")


def clean_dependents_data(dependents_data):
    """
    Filters out completely empty items from dependents_data.

    Considered invalid (and removed):
        - Empty dicts: [{}]
        - Non-dict types like [{""}], [{" "}]

    Considered valid (and kept):
        - Dicts with at least one key, even if value is empty (e.g., [{"name": ""}])

    :param dependents_data: list of dependent objects
    :return: cleaned list, or empty list if nothing valid
    """
    if not isinstance(dependents_data, list):
        return []

    def is_valid_dependent(dep):
        return isinstance(dep, dict) and bool(dep.keys())

    return [dep for dep in dependents_data if is_valid_dependent(dep)]


def application_movement_to_dol_dife_admin(application_id, status, action, role_name, user_str, application_to):

    match = re.search(r"\[([0-9a-fA-F-]{36})\]", user_str)
    user_created_uuid = match.group(1) if match else None
    user_instance = User.objects.get(id=user_created_uuid)
    core_user_obj = User.objects.get(id=user_created_uuid)
    application_from = core_user_obj.i_user_id
    role_instance = Role.objects.get(name=role_name)

    movement = WorkforceApplicationMovement(
        id=uuid.uuid4(),
        is_deleted=False,
        json_ext={},
        date_created=now,
        date_updated=now,
        note="",
        action=action,
        status=status,
        application_id=uuid.UUID(str(application_id)),
        user_created=user_instance,
        user_updated=user_instance,
        application_from_id=application_from,
        application_to_id=application_to,
        to_role=role_instance
    )
    movement.save(username=core_user_obj.username)
