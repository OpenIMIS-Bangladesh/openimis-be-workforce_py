import os
import logging
from django.core.files.storage import default_storage
from .file_services import delete_uploaded_file

from core.services import BaseService
from workforce.models import WorkforceDocument, InteractiveUser
from django.db.models import Q

logger = logging.getLogger(__name__)


class WorkforceDocumentServices(BaseService):
    OBJECT_TYPE = WorkforceDocument
    def get(self, **kwargs):
        filters = []
        model = self.OBJECT_TYPE

        client_mutation_id = kwargs.get("client_mutation_id", None)
        if client_mutation_id:
            filters.append(Q(json_ext__contains={"client_mutation_id": client_mutation_id}))

        query = model.objects.filter(*filters, is_deleted=False).all()
        return query

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