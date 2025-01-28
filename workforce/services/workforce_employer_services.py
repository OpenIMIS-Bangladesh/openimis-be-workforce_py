import logging

from core.services import BaseService
from location.models import Location
from core.models import InteractiveUser
from workforce.models import WorkforceEmployer, WorkforceRepresentative
from workforce.services.user_services import create_interactive_user

logger = logging.getLogger(__name__)


class WorkforceEmployerServices(BaseService):
    OBJECT_TYPE = WorkforceEmployer

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)

    def update_status(self, obj_data):
        if obj_data.get('id') and obj_data.get('status'):
            return super().update(obj_data)
