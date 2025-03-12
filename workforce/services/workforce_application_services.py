import logging

from core.services import BaseService
from workforce.models import WorkforceApplication

logger = logging.getLogger(__name__)


class WorkforceApplicationServices(BaseService):
    OBJECT_TYPE = WorkforceApplication

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
