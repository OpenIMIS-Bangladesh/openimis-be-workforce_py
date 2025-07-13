import os
import logging
from django.core.files.storage import default_storage
from .file_services import delete_uploaded_file

from core.services import BaseService
from workforce.models import WorkforceDocument, InteractiveUser

logger = logging.getLogger(__name__)


class WorkforceDocumentServices(BaseService):
    OBJECT_TYPE = WorkforceDocument

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        if obj_data.get('is_deleted'):
            doc_id = obj_data.get('id')
            if doc_id:
                try:
                    document = WorkforceDocument.objects.get(id=doc_id)
                    if document.path:
                        filename = os.path.basename(document.path)
                        delete_uploaded_file(filename)
                except WorkforceDocument.DoesNotExist:
                    logger.warning(f"Document not found with ID: {doc_id}")
        return super().update(obj_data)