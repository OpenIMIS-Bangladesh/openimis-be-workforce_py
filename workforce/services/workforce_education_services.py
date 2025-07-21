import logging

from core.services import BaseService
from workforce.models import WorkforceEducation

logger = logging.getLogger(__name__)


class WorkforceEducationServices(BaseService):
    OBJECT_TYPE = WorkforceEducation

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
