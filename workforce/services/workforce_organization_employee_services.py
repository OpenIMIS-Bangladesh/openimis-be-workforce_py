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
        location = Location.objects.get(pk=obj_data['location'])
        obj_data['location'] = location
        user = InteractiveUser.objects.get(uuid=obj_data['related_user'])
        obj_data['related_user'] = user

        return super().create(obj_data)

    def update(self, obj_data):
        location = Location.objects.get(pk=obj_data['location'])
        obj_data['location'] = location
        user = InteractiveUser.objects.get(uuid=obj_data['related_user'])
        obj_data['related_user'] = user

        return super().update(obj_data)
