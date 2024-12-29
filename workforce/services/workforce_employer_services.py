import logging

from core.services import BaseService
from location.models import Location
from core.models import InteractiveUser
from workforce.models import WorkforceEmployer, WorkforceRepresentative
from workforce.services.user_services import create_interactive_user

logger = logging.getLogger(__name__)


class WorkforceEmployerServices(BaseService):
    OBJECT_TYPE = WorkforceEmployer

    def create(self, obj_data):
        location = Location.objects.get(pk=obj_data['location'])
        obj_data['location'] = location
        workforce_representative = WorkforceRepresentative.objects.get(pk=obj_data['workforce_representative'])
        obj_data['workforce_representative'] = workforce_representative

        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
