import logging

from core.services import BaseService
from workforce.models import WorkforceDocumentMap

logger = logging.getLogger(__name__)


class WorkforceDocumentMapServices(BaseService):
    OBJECT_TYPE = WorkforceDocumentMap

    def create(self, obj_data):
        #delete existing:
        WorkforceDocumentMap.objects.filter(workforce_application_id= obj_data.get("workforce_application_id"), workforce_document_id= obj_data.get("workforce_document_id")).delete()
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
