import logging

from core.services import BaseService
from workforce.models import WorkforceEmployeeDependent

logger = logging.getLogger(__name__)


class WorkforceEmployeeDependentServices(BaseService):
    OBJECT_TYPE = WorkforceEmployeeDependent

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
