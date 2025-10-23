import re
import uuid
import logging
from django.apps import apps
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from core.models import Role
from core.services import BaseService


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


# def role_based_application_movement(application_id, action):
#     now = timezone.now()
#
#     movement = WorkforceApplicationMovement(
#         id=uuid.uuid4(),
#         is_deleted=False,
#         json_ext={},
#         date_created=now,
#         date_updated=now,
#         version=1,
#         note="আবেদন ডক্টরের কাছে প্রেরণ করা হয়েছে",
#         action=action,
#         status=action,
#         application_id=uuid.UUID(str(application_id)),
#         user_created=user_instance,
#         user_updated=user_instance,
#         application_from_id=application_from,
#         application_to_id=doc_id,
#         to_role=role_instance
#     )