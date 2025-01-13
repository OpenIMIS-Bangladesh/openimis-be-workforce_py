import logging

from core.services import BaseService
from core.models import InteractiveUser
from workforce.models import WorkforceOrganizationEmployeeDesignation, WorkforceOrganizationUnitDesignation, WorkforceOrganizationEmployee

logger = logging.getLogger(__name__)


class WorkforceOrganizationEmployeeDesignationServices(BaseService):
    OBJECT_TYPE = WorkforceOrganizationEmployeeDesignation

    def create(self, obj_data):
        designation = WorkforceOrganizationUnitDesignation.objects.get(pk=obj_data['designation'])
        obj_data['designation'] = designation
        employee = WorkforceOrganizationEmployee.objects.get(pk=obj_data['employee'])
        obj_data['employee'] = employee
        released_by = InteractiveUser.objects.get(uuid=obj_data['released_by'])
        obj_data['released_by'] = released_by
        status = obj_data['status'].lower()

        if status == 'true':
            obj_data['status'] = True
        else:
            obj_data['status'] = False

        return super().create(obj_data)

    def update(self, obj_data):
        designation = WorkforceOrganizationUnitDesignation.objects.get(pk=obj_data['designation'])
        obj_data['designation'] = designation
        employee = WorkforceOrganizationEmployee.objects.get(pk=obj_data['employee'])
        obj_data['employee'] = employee
        released_by = InteractiveUser.objects.get(uuid=obj_data['released_by'])
        obj_data['released_by'] = released_by

        return super().update(obj_data)
