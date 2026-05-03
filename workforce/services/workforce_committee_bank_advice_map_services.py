import logging
import base64

from core.models.user import UserRole, InteractiveUser
from core.services import BaseService
from django.db import IntegrityError

from workforce.models import WorkforceCommitteeUserMap, WorkforceCommittee, WorkforceCommitteeUser, \
    WorkforceCommitteeBankAdviceMap

logger = logging.getLogger(__name__)

def extract_uuid(encoded_str):
    decoded = base64.b64decode(encoded_str).decode()
    return decoded.split(":")[1]

class WorkforceCommitteeBankAdviceMapServices(BaseService):
    OBJECT_TYPE = WorkforceCommitteeBankAdviceMap

    def create(self, obj_data):
        obj_data["user_created"] = self.user
        return super().create(obj_data)



    def update(self, obj_data):
        obj_data["user_updated"] = self.user
        return super().update(obj_data)

    def delete(self, obj_data):
        return super().delete(obj_data)
