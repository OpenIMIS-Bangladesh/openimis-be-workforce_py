import logging

from core.services import BaseService
from workforce.models import WorkforceDocument, InteractiveUser

logger = logging.getLogger(__name__)


class WorkforceDocumentServices(BaseService):
    OBJECT_TYPE = WorkforceDocument

    def create(self, obj_data):
        # verifier = InteractiveUser.objects.get(id=obj_data.get('verifier'))
        # obj_data['verifier'] = verifier
        # approver = InteractiveUser.objects.get(id=obj_data.get('approver'))
        # obj_data['approver'] = approver
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
