import logging
import base64

from core.models.user import UserRole
from core.services import BaseService
from django.db import IntegrityError

from workforce.models import WorkforceCommitteeUserMap, WorkforceCommittee

logger = logging.getLogger(__name__)

def extract_uuid(encoded_str):
    decoded = base64.b64decode(encoded_str).decode()
    return decoded.split(":")[1]

class WorkforceCommitteeUserMapServices(BaseService):
    OBJECT_TYPE = WorkforceCommitteeUserMap

    def create(self, obj_data):
        # obj_data["user_created"] = self.user
        # return super().create(obj_data)
        committee_id= obj_data["committee_id"]
        user_id= obj_data["user_id"]
        committee = WorkforceCommittee.objects.get(id=committee_id)
        new_map= WorkforceCommitteeUserMap(committee_id=committee_id, user_id=user_id, is_noa_signature_user=False)
        try:
            new_map.save(username=self.user.username)
            new_user_role= UserRole(
                user_id=user_id,
                role_id=committee.assigned_role_id,
                audit_user_id=1
            )
            new_user_role.save()
        except IntegrityError as e:
            return None


    def update(self, obj_data):
        obj_data["user_updated"] = self.user
        return super().update(obj_data)

    def delete(self, obj_data):
        return super().delete(obj_data)
