import logging

from core.services import BaseService
from workforce.models import WorkforceEmployeeDesignation

logger = logging.getLogger(__name__)


class WorkforceEmployeeDesignationServices(BaseService):
    OBJECT_TYPE = WorkforceEmployeeDesignation

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
