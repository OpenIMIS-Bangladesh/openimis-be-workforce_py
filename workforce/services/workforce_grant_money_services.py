import logging

from core.services import BaseService
from workforce.models import WorkforceGrantMoney

logger = logging.getLogger(__name__)


class WorkforceGrantMoneyServices(BaseService):
    OBJECT_TYPE = WorkforceGrantMoney

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
