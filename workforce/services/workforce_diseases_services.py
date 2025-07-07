import logging

from core.services import BaseService
from workforce.models import WorkforceDiseases

logger = logging.getLogger(__name__)


class WorkforceDiseasesServices(BaseService):
    OBJECT_TYPE = WorkforceDiseases

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
