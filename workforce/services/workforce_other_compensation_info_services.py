import logging

from core.services import BaseService
from location.models import Location
from core.models import InteractiveUser
from workforce.models import WorkforceOtherCompensationInfo
from workforce.services.user_services import create_interactive_user

logger = logging.getLogger(__name__)


class WorkforceOtherCompensationInfoServices(BaseService):
    OBJECT_TYPE = WorkforceOtherCompensationInfo

    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)

