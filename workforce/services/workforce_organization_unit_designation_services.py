import logging

from core.services import BaseService
from location.models import Location
from workforce.models import WorkforceOrganizationUnitDesignation

logger = logging.getLogger(__name__)


class WorkforceOrganizationUnitDesignationServices(BaseService):
    OBJECT_TYPE = WorkforceOrganizationUnitDesignation

    def create(self, obj_data):

        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
