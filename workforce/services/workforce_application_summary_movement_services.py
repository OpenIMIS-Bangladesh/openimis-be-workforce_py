import logging

from core.services import BaseService
from workforce.models import WorkforceApplicationSummaryMovement

logger = logging.getLogger(__name__)


class WorkforceApplicationSummaryMovementServices(BaseService):
    OBJECT_TYPE = WorkforceApplicationSummaryMovement

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
