import logging

from core.services import BaseService
from workforce.models import WorkforceApplicationMovement

logger = logging.getLogger(__name__)


class WorkforceApplicationMovementServices(BaseService):
    OBJECT_TYPE = WorkforceApplicationMovement

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        status = obj_data.get("status")
        if status == "forward_to_doctor":
            print("=================?")
            print("{condition met, ignoring....")
            pass
        return super().update(obj_data)
