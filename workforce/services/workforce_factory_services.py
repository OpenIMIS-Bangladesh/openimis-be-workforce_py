import logging

from core.services import BaseService
from location.models import Location
from workforce.models import WorkforceFactory, WorkforceEmployer, WorkforceRepresentative

logger = logging.getLogger(__name__)


class WorkforceFactoryServices(BaseService):
    OBJECT_TYPE = WorkforceFactory

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
