import logging

from core.services import BaseService
from workforce.models import WorkforceEmployeeAccident

logger = logging.getLogger(__name__)


class WorkforceEmployeeAccidentServices(BaseService):
    OBJECT_TYPE = WorkforceEmployeeAccident

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
