import logging

from core.services import BaseService
from workforce.models import WorkforceNotification

logger = logging.getLogger(__name__)


class WorkforceNotificationServices(BaseService):
    OBJECT_TYPE = WorkforceNotification

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
