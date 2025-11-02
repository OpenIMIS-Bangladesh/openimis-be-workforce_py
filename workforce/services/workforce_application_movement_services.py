import logging

from core.services import BaseService
from workforce.models import WorkforceApplicationMovement

logger = logging.getLogger(__name__)


class WorkforceApplicationMovementServices(BaseService):
    OBJECT_TYPE = WorkforceApplicationMovement

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
