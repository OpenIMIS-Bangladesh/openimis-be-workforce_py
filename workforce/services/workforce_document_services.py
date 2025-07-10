import logging

from core.services import BaseService
from workforce.models import WorkforceDocument, InteractiveUser

logger = logging.getLogger(__name__)


class WorkforceDocumentServices(BaseService):
    OBJECT_TYPE = WorkforceDocument

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)

    def delete(self, obj_data):
        return super().delete(obj_data)