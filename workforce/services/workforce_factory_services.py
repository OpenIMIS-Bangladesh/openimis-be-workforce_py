import logging

from core.services import BaseService
from location.models import Location
from workforce.models import WorkforceFactory, WorkforceEmployer, WorkforceRepresentative

logger = logging.getLogger(__name__)


class WorkforceFactoryServices(BaseService):
    OBJECT_TYPE = WorkforceFactory

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
