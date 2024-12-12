import logging

from core.services import BaseService
from location.models import Location
from workforce.models import WorkforceOrganization

logger = logging.getLogger(__name__)


class WorkforceOrganizationServices(BaseService):
    OBJECT_TYPE = WorkforceOrganization

    def create(self, obj_data):
        location = obj_data['location']
        location = Location.objects.get(pk=location)
        obj_data['location'] = location

        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
