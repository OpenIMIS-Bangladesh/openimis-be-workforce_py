from core.services.userServices import create_or_update_interactive_user
import logging
import uuid

from workforce.models import WorkforceUser

logger = logging.getLogger(__name__)


class WorkforceUserServices():
    OBJECT_TYPE = WorkforceUser

    def create(self, obj_data):
        data = {
            "username": obj_data.get('nid'),
            "other_names": ' ',
            "last_name": obj_data.get('last_name_en'),
            "phone": obj_data.get('phone_number'),
            "email": '',
            "language": 'en',
            "health_facility_id": 1,
            "password": obj_data.get('password'),
            "roles": obj_data.get("roles", []),
        }

        create_or_update_interactive_user(None, data, 1, False)

        user_obj = WorkforceUser.objects.create(
            name_bn=obj_data.get("name_bn"),
            first_name_en=obj_data.get("first_name_en"),
            last_name_en=obj_data.get("last_name_en"),
            nid=obj_data.get("nid"),
            phone_number=obj_data.get("phone_number"),
            status=obj_data.get("status"),
        )

        return {"internal_id": str(uuid.uuid4())}

    def update(self, obj_data):
        return super().update(obj_data)
