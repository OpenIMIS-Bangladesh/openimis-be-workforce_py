import logging

from core.services import BaseService
from location.models import Location
from workforce.models import WorkforceFactory, WorkforceEmployer
from django.db.models import Q

logger = logging.getLogger(__name__)


class WorkforceFactoryServices(BaseService):
    OBJECT_TYPE = WorkforceFactory

    def get(self, **kwargs):
        filters = []
        model = self.OBJECT_TYPE

        client_mutation_id = kwargs.get("client_mutation_id", None)
        if client_mutation_id:
            filters.append(Q(json_ext__contains={"client_mutation_id": client_mutation_id}))

        query = model.objects.filter(*filters, is_deleted=False).all()
        return query

    def create(self, obj_data):
        if obj_data.get('is_same_company_representative') == "1":
            representative = WorkforceEmployer.objects.get(id=obj_data.get('workforce_employer_id'))
            representative_id = representative.workforce_representative_id
        else:
            representative_id = obj_data.get('workforce_representative_id')

        obj_data['workforce_representative_id'] = representative_id
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
