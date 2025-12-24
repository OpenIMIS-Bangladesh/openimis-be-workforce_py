import logging

from core.services import BaseService
from workforce.models import WorkforceAllAssociation

logger = logging.getLogger(__name__)


class WorkforceAllAssociationServices(BaseService):
    OBJECT_TYPE = WorkforceAllAssociation

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)

