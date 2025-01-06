import logging

from core.services import BaseService
from core.models import InteractiveUser
from location.models import Location
from workforce.models import WorkforceEmployee, WorkforceEmployer

logger = logging.getLogger(__name__)


class WorkforceEmployeeServices(BaseService):
    OBJECT_TYPE = WorkforceEmployee

    def create(self, obj_data):
        employer_id = WorkforceEmployer.objects.get(pk=obj_data['employer_id'])
        obj_data['employer_id'] = employer_id
        present_location = Location.objects.get(pk=obj_data['present_location'])
        obj_data['present_location'] = present_location
        permanent_location = Location.objects.get(pk=obj_data['permanent_location'])
        obj_data['permanent_location'] = permanent_location
        related_user = InteractiveUser.objects.get(uuid=obj_data['related_user'])
        obj_data['related_user'] = related_user

        return super().create(obj_data)

    def update(self, obj_data):
        employer_id = WorkforceEmployer.objects.get(pk=obj_data['employer_id'])
        obj_data['employer_id'] = employer_id
        present_location = Location.objects.get(pk=obj_data['present_location'])
        obj_data['present_location'] = present_location
        permanent_location = Location.objects.get(pk=obj_data['permanent_location'])
        obj_data['permanent_location'] = permanent_location
        related_user = InteractiveUser.objects.get(uuid=obj_data['related_user'])
        obj_data['related_user'] = related_user

        return super().update(obj_data)
