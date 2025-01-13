import logging

from core.services import BaseService
from core.models import InteractiveUser
from location.models import Location
from workforce.models import WorkforceEmployee, WorkforceEmployer

logger = logging.getLogger(__name__)


class WorkforceEmployeeServices(BaseService):
    OBJECT_TYPE = WorkforceEmployee

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
