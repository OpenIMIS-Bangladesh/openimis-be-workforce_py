import logging

from core.models.user import InteractiveUser
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

        create_notification= WorkforceNotification(
            notification="You received a new Application from: "+ (from_user_id.last_name if from_user_id is not None else "EIS Coordinator"),
            status=obj_data.get("status"),
            user_id=to_user_id if to_user_id is not None else None,
            is_read= False,
        )
        create_notification.save(username=self.user.username)
        return obj_data

    def update(self, obj_data):
        return super().update(obj_data)
