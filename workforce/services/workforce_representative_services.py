import logging

from core.models import InteractiveUser
from core.services import BaseService
from location.models import Location
from workforce.models import WorkforceRepresentative
from datetime import date

logger = logging.getLogger(__name__)


class WorkforceRepresentativeServices(BaseService):
    OBJECT_TYPE = WorkforceRepresentative

    def create(self, obj_data):
        location = Location.objects.get(pk=obj_data['location'])
        user_id = obj_data.pop('user_id')
        user = InteractiveUser.objects.get(pk=user_id)
        obj_data['location'] = location
        obj_data['related_user'] = user
        
        # birth_date = obj_data['birth_date']
        # birth_date = date.isoformat(birth_date)
        # obj_data['birth_date'] = birth_date

        super().create(obj_data)
