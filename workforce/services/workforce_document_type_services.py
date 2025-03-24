import logging

from core.services import BaseService
from workforce.models import WorkforceDocumentType

logger = logging.getLogger(__name__)


class WorkforceDocumentTypeServices(BaseService):
    OBJECT_TYPE = WorkforceDocumentType

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
