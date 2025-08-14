import logging

from core.services import BaseService
from workforce.models import WorkforceSignature

logger = logging.getLogger(__name__)


class WorkforceSignatureServices(BaseService):
    OBJECT_TYPE = WorkforceSignature

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
