import logging

from core.services import BaseService
from core.models import InteractiveUser
from location.models import Location
from workforce.models import WorkforceEmployee, WorkforceEmployer, WorkforceEmployeeDesignation
from workforce.services.user_services import delete_interactive_user, create_interactive_user

logger = logging.getLogger(__name__)


class WorkforceEmployeeServices(BaseService):
    OBJECT_TYPE = WorkforceEmployee

    def create(self, obj_data):
        if obj_data.get('related_user_id') and obj_data.get('related_user_id') != '':
            user = obj_data['related_user_id']
        else:
            create_user = create_interactive_user(obj_data.get('first_name_en'), obj_data.get('last_name_en'),
                                                  obj_data.get('nid'), obj_data.get('role_id', 0))
            user = create_user.id

        obj_data['related_user_id'] = user
        created_obj = super().create(obj_data)

        if created_obj is not None and created_obj.get("success") is False and not obj_data.get('related_user_id'):
            delete_interactive_user(user)

        return created_obj

    def update(self, obj_data):
        return super().update(obj_data)
