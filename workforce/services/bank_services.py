import logging

from core.services import BaseService
from workforce.models import Bank

logger = logging.getLogger(__name__)


class BankServices(BaseService):
    OBJECT_TYPE = Bank

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
