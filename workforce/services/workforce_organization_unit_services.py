import logging

from core.services import BaseService
from workforce.models import WorkforceOrganizationUnit, WorkforceOrganization

logger = logging.getLogger(__name__)


class WorkforceOrganizationUnitServices(BaseService):
    OBJECT_TYPE = WorkforceOrganizationUnit

    def create(self, obj_data):
        organization = WorkforceOrganization.objects.get(pk=obj_data['organization'])
        obj_data['organization'] = organization
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
