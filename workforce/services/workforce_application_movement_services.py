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
        super().create(obj_data)
        from_user_id= InteractiveUser.objects.get(id=obj_data.get("application_from_id")) if obj_data.get("application_from_id") is not None else None
        to_user_id= InteractiveUser.objects.get(id=obj_data.get("application_to_id")) if obj_data.get("application_to_id") is not None else None

        from_role_id= UserRole.objects.filter(user_id=from_user_id).first().role_id or None
        role= Role.objects.get(id= from_role_id) if from_role_id is not None else None

        create_notification= WorkforceNotification(
            notification="You have received an application to work on from: "+ (from_user_id.last_name if from_user_id is not None else "EIS Coordinator") + (" ("+role.name+")" if role else ""),
            notification_bn="আপনি "+ (from_user_id.other_names if from_user_id is not None else "EIS Coordinator")  + (" ("+role.name+")" if role else "") + " হতে একটি আবেদনপত্র রিসিভ করেছেন।",
            status=obj_data.get("status"),
            user_id=to_user_id.id if to_user_id is not None else None,
            is_read= False,
        )
        create_notification.save(username=self.user.username)
        return obj_data

    def update(self, obj_data):
        return super().update(obj_data)
