import logging

from core.services import BaseService

from workforce.models import WorkforceCommitteeUser
from workforce.services.user_services import create_interactive_user, update_interactive_user
from core.models.user import User, UserRole, InteractiveUser

logger = logging.getLogger(__name__)


class WorkforceCommitteeUserServices(BaseService):
    OBJECT_TYPE = WorkforceCommitteeUser
    def create(self, obj_data):
        create_user = create_interactive_user(obj_data.get('representative_name'),
                                              obj_data.get('representative_name_bn', obj_data.get('representative_name', "-")),
                                              obj_data.get('login_name', obj_data.get('email')), 0)
        user = create_user.id
        obj_data["related_user_id"] = user
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)

