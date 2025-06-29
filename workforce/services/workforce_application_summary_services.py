import logging
import json
from django.db.models import Q
from django.core.exceptions import ValidationError

from core.services import BaseService
from workforce.models import WorkforceApplicationSummary

logger = logging.getLogger(__name__)


class WorkforceApplicationSummaryServices(BaseService):
    OBJECT_TYPE = WorkforceApplicationSummary

    def get(self, **kwargs):
        filters = []
        model = self.OBJECT_TYPE

        client_mutation_id = kwargs.get("client_mutation_id", None)
        if client_mutation_id:
            filters.append(Q(json_ext__contains={"client_mutation_id": client_mutation_id}))

        query = model.objects.filter(*filters, is_deleted=False).all()
        return query

    def create(self, obj_data):
        application_data = obj_data.get("application_data") or {}

        if isinstance(application_data, str):
            try:
                application_data = json.loads(application_data)
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid JSON in application_data: {str(e)}")

        obj_data["application_data"] = application_data

        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
