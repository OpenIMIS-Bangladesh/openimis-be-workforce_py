import logging
import random
from core.services import BaseService
from workforce.models import WorkforceApplication
from django.db.models import Q


logger = logging.getLogger(__name__)


class WorkforceApplicationServices(BaseService):
    OBJECT_TYPE = WorkforceApplication

    def get(self, **kwargs):
        filters = []
        model = self.OBJECT_TYPE

        client_mutation_id = kwargs.get("client_mutation_id", None)
        if client_mutation_id:
            filters.append(Q(json_ext__contains={"client_mutation_id": client_mutation_id}))

        query = model.objects.filter(*filters, is_deleted=False).order_by('-date_created')
        return query

    def create(self, obj_data):
        phone_number = obj_data.get("phone_number")
        if phone_number:
            tracking_number = phone_number + str(random.randint(0,99)).zfill(2)
            obj_data["tracking_number"] = tracking_number
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
