import logging

from core.services import BaseService
from workforce.models import WorkforceEmployeeAccountInfo

logger = logging.getLogger(__name__)


class WorkforceEmployeeAccountInfoServices(BaseService):
    OBJECT_TYPE = WorkforceEmployeeAccountInfo

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
