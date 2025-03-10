import logging

from core.services import BaseService
from workforce.models import WorkforceTemporaryApplication

logger = logging.getLogger(__name__)


class WorkforceTemporaryApplicationServices(BaseService):
    OBJECT_TYPE = WorkforceTemporaryApplication

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
