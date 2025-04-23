from core.services.userServices import create_or_update_interactive_user
import logging
import uuid

from workforce.models import WorkforceUser

logger = logging.getLogger(__name__)


class WorkforceUserServices:
    OBJECT_TYPE = WorkforceUser

    def create(self, obj_data):
        data = {
            # "login_name": obj_data.get('nid') or ' ',
            "username": obj_data.get('nid') or 'test_username',
            "other_names": ' ',
            "last_name": obj_data.get('last_name_en'),
            "phone": obj_data.get('phone_number'),
            "email": '',
            "language": 'en',
            "health_facility_id": 1,
            "password": obj_data.get('password'),
        }
        create_or_update_interactive_user(None, data, 1, False)
        obj_data["internal_id"] = str(uuid.uuid4())
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
