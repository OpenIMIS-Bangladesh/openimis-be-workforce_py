import logging

from core.services import BaseService
from workforce.models import WorkforceAllAssociation

logger = logging.getLogger(__name__)


class WorkforceAllAssociationServices(BaseService):
    OBJECT_TYPE = WorkforceAllAssociation

    def create(self, obj_data):
        obj_data["user_created"] = self.user
        return super().create(obj_data)

    def update(self, obj_data):
        obj_data["user_updated"] = self.user
        return super().update(obj_data)

