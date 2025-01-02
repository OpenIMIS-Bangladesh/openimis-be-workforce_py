import logging

from core.services import BaseService
from location.models import Location
from workforce.models import WorkforceOffice, WorkforceEmployer, WorkforceRepresentative

logger = logging.getLogger(__name__)


class WorkforceOfficeServices(BaseService):
    OBJECT_TYPE = WorkforceOffice

    def create(self, obj_data):
        workforce_employer = WorkforceEmployer.objects.get(pk=obj_data['workforce_employer'])
        obj_data['workforce_employer'] = workforce_employer
        location = Location.objects.get(pk=obj_data['location'])
        obj_data['location'] = location
        workforce_representative = WorkforceRepresentative.objects.get(pk=obj_data['workforce_representative'])
        obj_data['workforce_representative'] = workforce_representative
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
