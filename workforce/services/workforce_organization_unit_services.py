import logging

from core.services import BaseService
from location.models import Location
from workforce.models import WorkforceOrganizationUnit

logger = logging.getLogger(__name__)


class WorkforceOrganizationUnitServices(BaseService):
    OBJECT_TYPE = WorkforceOrganizationUnit

    def create(self, obj_data):

        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
