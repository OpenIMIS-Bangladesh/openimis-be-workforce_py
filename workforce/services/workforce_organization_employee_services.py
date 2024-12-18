import logging

from core.services import BaseService
from location.models import Location
from core.models import InteractiveUser
from workforce.models import WorkforceOrganizationEmployee, WorkforceOrganizationUnitDesignation
from workforce.services.user_services import create_interactive_user

logger = logging.getLogger(__name__)


class WorkforceOrganizationEmployeeServices(BaseService):
    OBJECT_TYPE = WorkforceOrganizationEmployee

    def create(self, obj_data):
        designation = WorkforceOrganizationUnitDesignation.objects.get(pk=obj_data['designation'])
        obj_data['designation'] = designation
        location = Location.objects.get(pk=obj_data['location'])
        obj_data['location'] = location
        if obj_data.get('user_id') and obj_data.get('user_id') != '':
            user = InteractiveUser.objects.get(pk=obj_data['user_id'])
        else:
            user = create_interactive_user(obj_data.get('name_en'), obj_data.get('name_bn'), obj_data.get('email'), 800)

        obj_data['related_user'] = user

        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
