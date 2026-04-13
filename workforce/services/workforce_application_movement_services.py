import logging

from core.models.user import InteractiveUser
from core.models.user import UserRole
from core.models.user import Role
from core.services import BaseService
from workforce.models import WorkforceApplicationMovement
from workforce.models import WorkforceNotification

logger = logging.getLogger(__name__)


class WorkforceApplicationMovementServices(BaseService):
    OBJECT_TYPE = WorkforceApplicationMovement

    def create(self, obj_data):
        # Step 1: Always create movement
        result = super().create(obj_data)

        try:
            from_user_id = InteractiveUser.objects.get(id=obj_data.get("application_from_id")) \
                if obj_data.get("application_from_id") else None

            to_user_id = InteractiveUser.objects.get(id=obj_data.get("application_to_id")) \
                if obj_data.get("application_to_id") else None

            from_role = UserRole.objects.filter(user_id=from_user_id).first()
            role = Role.objects.get(id=from_role.role_id) if from_role else None

            to_role_id= obj_data.get("to_role_id", None)
            if to_user_id is None:
                users_by_role= UserRole.objects.filter(role_id=to_role_id).first()
                to_user_id = users_by_role.user

            notification = WorkforceNotification(
                notification="You have received an application to work on from: " +
                             (from_user_id.last_name if from_user_id else "EIS Coordinator") +
                             (" (" + role.name + ")" if role else ""),
                notification_bn="আপনি " +
                                (from_user_id.other_names if from_user_id else "EIS Coordinator") +
                                (" (" + role.name + ")" if role else "") +
                                " হতে একটি আবেদনপত্র রিসিভ করেছেন।",
                status=obj_data.get("status"),
                user_id=to_user_id.id if to_user_id else None,
                workforce_application_id=obj_data.get("application_id"),
                is_read=False,
            )

            notification.save(username=self.user.username)

        except Exception as e:
            # Don't break the flow — just log it
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Notification creation failed: {str(e)}")

        return result

    def update(self, obj_data):
        return super().update(obj_data)
