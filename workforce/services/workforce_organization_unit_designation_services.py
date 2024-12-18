import logging

from core.services import BaseService
from location.models import Location
from workforce.models import WorkforceOrganizationUnitDesignation, WorkforceOrganization, WorkforceOrganizationUnit

logger = logging.getLogger(__name__)


class WorkforceOrganizationUnitDesignationServices(BaseService):
    OBJECT_TYPE = WorkforceOrganizationUnitDesignation

    def create(self, obj_data):
        organization = WorkforceOrganization.objects.get(pk=obj_data['organization'])
        obj_data['organization'] = organization
        organization_unit = WorkforceOrganizationUnit.objects.get(pk=obj_data['organization_unit'])
        obj_data['organization_unit'] = organization_unit

        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
