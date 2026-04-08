import logging

from core.services import BaseService

from workforce.models import WorkforceCommitteeUser
from workforce.services.user_services import create_interactive_user, update_interactive_user

logger = logging.getLogger(__name__)


class WorkforceCommitteeUserServices(BaseService):
    OBJECT_TYPE = WorkforceCommitteeUser

    def create(self, obj_data):
        if obj_data.get("related_user_id") and obj_data.get("related_user_id") != "":
            related_user_id = obj_data["related_user_id"]
        else:
            created_user = create_interactive_user(
                obj_data.get("representative_name"),
                obj_data.get("organization_name"),
                obj_data.get("login_name"),
                0,
            )
            related_user_id = created_user.id

        obj_data["related_user_id"] = related_user_id
        return super().create(obj_data)

    def update(self, obj_data):
        related_user_id = obj_data.get("related_user_id")
        if related_user_id:
            update_interactive_user(
                related_user_id,
                obj_data.get("representative_name"),
                obj_data.get("organization_name"),
            )
        return super().update(obj_data)

