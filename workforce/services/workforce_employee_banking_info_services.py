import logging

from core.services import BaseService
from core.models import InteractiveUser
from workforce.models import WorkforceEmployeeBankingInfo

logger = logging.getLogger(__name__)


class WorkforceEmployeeBankingInfoServices(BaseService):
    OBJECT_TYPE = WorkforceEmployeeBankingInfo

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
