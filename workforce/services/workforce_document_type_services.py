import logging

from core.services import BaseService
from workforce.models import WorkforceDocumentType

logger = logging.getLogger(__name__)


class WorkforceDocumentTypeServices(BaseService):
    OBJECT_TYPE = WorkforceDocumentType

    def get(self, **kwargs):
        filters = []
        model = self.OBJECT_TYPE

        query = model.objects.filter(*filters, is_deleted=False).all()
        return query

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
