import logging

from core.services import BaseService
from workforce.models import WorkforceAssociationUserMap

logger = logging.getLogger(__name__)


class WorkforceAssociationUserMapServices(BaseService):
    OBJECT_TYPE = WorkforceAssociationUserMap

    def create(self, obj_data):
        obj_data["user_created"] = self.user
        if WorkforceAssociationUserMap.objects.filter(all_association_id= obj_data["all_association_id"], user_id= obj_data["user_id"], is_deleted=False).exists():
            return False
        else:
            return super().create(obj_data)

    def update(self, obj_data):
        obj_data["user_updated"] = self.user
        return super().update(obj_data)


    def delete(self, obj_data):
        print(obj_data)
        WorkforceAssociationUserMap.objects.get(id = obj_data["map_id"]).delete()