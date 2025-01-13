import logging
import json

from core.services import BaseService
from location.models import Location
from core.models import InteractiveUser
from workforce.models import WorkforceOrganizationEmployee
from workforce.services.user_services import create_interactive_user

logger = logging.getLogger(__name__)


class WorkforceOrganizationEmployeeServices(BaseService):
    OBJECT_TYPE = WorkforceOrganizationEmployee

    def create(self, obj_data):
        if obj_data.get('related_user_id') and obj_data.get('related_user_id') != '':
            user = obj_data['related_user_id']
        else:
            create_user = create_interactive_user(
                obj_data.get('name_en'),
                obj_data.get('name_bn'),
                obj_data.get('email'), 800
            )
            user = create_user.id

        obj_data['related_user_id'] = user

        created_obj = super().create(obj_data)

        if created_obj is not None:
            if created_obj.get("success") is False:
                user.delete()

        return created_obj

    def update(self, obj_data):
        return super().update(obj_data)
