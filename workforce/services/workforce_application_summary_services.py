import logging

from core.services import BaseService
from workforce.models import WorkforceApplicationSummary

logger = logging.getLogger(__name__)


class WorkforceApplicationSummaryServices(BaseService):
    OBJECT_TYPE = WorkforceApplicationSummary

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
