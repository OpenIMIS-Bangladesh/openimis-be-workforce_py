import logging

from core.services import BaseService
from core.models import InteractiveUser
from workforce.models import WorkforceOrganizationEmployeeDesignation, WorkforceOrganizationUnitDesignation, WorkforceOrganizationEmployee

logger = logging.getLogger(__name__)


class WorkforceOrganizationEmployeeDesignationServices(BaseService):
    OBJECT_TYPE = WorkforceOrganizationEmployeeDesignation

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
