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
        holder_id = obj_data.get("holder_id")
        path= obj_data.get("path")
        url= obj_data.get("url")
        document_type_id = obj_data.get("workforce_document_type_id")
        app_id = obj_data.get("workforce_application_id")

        if not holder_id and app_id and document_type_id:
            existing_doc = WorkforceDocument.objects.filter(
                workforce_document_type_id = document_type_id,
                workforce_application_id = app_id,
                is_deleted = False
            ).first()
            if existing_doc:
                obj_data["id"]= existing_doc.id
                return super().update(obj_data)
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