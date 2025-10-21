import re
import uuid
import logging
from django.apps import apps
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from core.models import Role
from core.services import BaseService

logger = logging.getLogger(__name__)

_DOCTOR_APP_TYPES = {
    "medicalAssistance",
    "maternityGrant",
    "disabilityAssistance",
    "medicalDonation",
}

_ORG_ROLE_MAP = {
    "cf": "cf_doctor",
    "blwf": "blwf_doctor",
    "eis": "eis_doctor",
}


class WorkforceApplicationBulkMovementServices(BaseService):
    """
    Handles bulk forwarding of Workforce Applications to doctors
    based on organization type and application type.
    """

    def bulk_forward_to_doctors(self, application_ids, action="forward_to_doctor", requesting_user=None):

        WorkforceApplication = apps.get_model("workforce", "WorkforceApplication")
        WorkforceApplicationMovement = apps.get_model("workforce", "WorkforceApplicationMovement")
        UserRole = apps.get_model("core", "UserRole")
        User = apps.get_model("core", "User")

        if not application_ids:
            raise ValidationError("No application IDs provided for bulk forward.")

        if isinstance(application_ids, dict):
            application_ids_list = application_ids.get("application_ids", [])
        else:
            application_ids_list = application_ids

        try:
            application_ids_list = [uuid.UUID(str(aid)) for aid in application_ids_list]
        except Exception as e:
            raise ValidationError(f"Invalid UUID in application_ids: {e}")

        user_str = str(self.user)
        match = re.search(r"\[([0-9a-fA-F-]{36})\]", user_str)
        user_created_uuid = match.group(1) if match else None
        core_user_obj = User.objects.get(id=user_created_uuid)
        application_from = core_user_obj.i_user_id

        try:
            user_instance = User.objects.get(id=user_created_uuid)
        except User.DoesNotExist:
            raise ValidationError(f"User with UUID {user_created_uuid} does not exist.")

        now = timezone.now()

        apps_qs = WorkforceApplication.objects.filter(id__in=application_ids_list)
        apps_by_org = {}
        errors = []

        for app in apps_qs:
            if app.application_type not in _DOCTOR_APP_TYPES:
                errors.append({
                    "id": str(app.id),
                    "skipped_reason": f"Not eligible type: {app.application_type}",
                })
                continue

            org = (app.organization_type or "").lower()
            role_name = _ORG_ROLE_MAP.get(org)
            if not role_name:
                errors.append({
                    "id": str(app.id),
                    "skipped_reason": f"No doctor role mapped for organization '{app.organization_type}'",
                })
                continue

            apps_by_org.setdefault(role_name, []).append(app)

        created_movements = []
        assignments_by_doctor = {}

        with transaction.atomic():
            for role_name, apps_list in apps_by_org.items():
                try:
                    role_instance = Role.objects.get(name=role_name)

                except UserRole.DoesNotExist:
                    errors.append({
                        "role_name": role_name,
                        "error": f"Role '{role_name}' not found in core_role table.",
                    })
                    continue
                # Find all doctors with this role
                doctor_user_ids = list(
                    UserRole.objects.filter(role__name=role_name)
                    .values_list("user_id", flat=True)
                    .distinct()
                )

                if not doctor_user_ids:
                    for a in apps_list:
                        errors.append({
                            "id": str(a.id),
                            "error": f"No doctors found for role '{role_name}'.",
                        })
                    continue

                # Distribute applications evenly among doctors
                doctor_user_ids = sorted(doctor_user_ids)
                n_docs = len(doctor_user_ids)
                n_apps = len(apps_list)
                base = n_apps // n_docs
                rem = n_apps % n_docs

                counts = [base] * n_docs
                for i in range(rem):
                    counts[i] += 1

                cursor = 0
                assignments_local = {doc_id: [] for doc_id in doctor_user_ids}
                for i_doc, doc_id in enumerate(doctor_user_ids):
                    c = counts[i_doc]
                    slice_apps = apps_list[cursor: cursor + c]
                    cursor += c
                    assignments_local[doc_id] = [a.id for a in slice_apps]

                # Create movement records
                for doc_id, assigned_app_ids in assignments_local.items():
                    for aid in assigned_app_ids:
                        movement = WorkforceApplicationMovement(
                            id=uuid.uuid4(),
                            is_deleted=False,
                            json_ext={},
                            date_created=now,
                            date_updated=now,
                            version=1,
                            note="আবেদন ডক্টরের কাছে প্রেরণ করা হয়েছে",
                            action=action,
                            status=action,
                            application_id=uuid.UUID(str(aid)),
                            user_created=user_instance,
                            user_updated=user_instance,
                            application_from_id=application_from,
                            application_to_id=doc_id,
                            to_role=role_instance
                        )
                        created_movements.append(movement)
                        assignments_by_doctor.setdefault(str(doc_id), []).append(str(aid))
                WorkforceApplication.objects.filter(
                    id__in=[a.id for a in apps_list]
                ).update(status=action)

            if created_movements:
                WorkforceApplicationMovement.objects.bulk_create(created_movements)
                logger.info(f"Created {len(created_movements)} movement records.")

        summary = {
            "created_movements_count": len(created_movements),
            "assignments_by_doctor": assignments_by_doctor,
            "errors": errors,
        }

        logger.info("Bulk forward completed successfully.")
        return summary
