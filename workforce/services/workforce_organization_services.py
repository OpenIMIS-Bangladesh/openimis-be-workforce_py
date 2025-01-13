import logging

from core.services import BaseService
from location.models import Location
from workforce.models import WorkforceOrganization

logger = logging.getLogger(__name__)


class WorkforceOrganizationServices(BaseService):
    OBJECT_TYPE = WorkforceOrganization

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        super().update(obj_data)
