import logging

from core.models import InteractiveUser
from core.services import BaseService
from location.models import Location
from django.db.models import Q
from workforce.models import WorkforceRepresentative
from workforce.services.user_services import create_interactive_user

logger = logging.getLogger(__name__)


class WorkforceRepresentativeServices(BaseService):
    OBJECT_TYPE = WorkforceRepresentative

    def get(self, **kwargs):
        filters = []
        model = self.OBJECT_TYPE

        client_mutation_id = kwargs.get("client_mutation_id", None)
        if client_mutation_id:
            filters.append(Q(json_ext__contains={"client_mutation_id": client_mutation_id}))

        query = model.objects.filter(*filters, is_deleted=False).all()
        return query

    def create(self, obj_data):
        location = Location.objects.get(pk=obj_data['location'])
        obj_data['location'] = location

        if obj_data.get('user_id') and obj_data.get('user_id') != '':
            user = InteractiveUser.objects.get(pk=obj_data['user_id'])
        else:
            user = create_interactive_user(obj_data.get('name_en'), obj_data.get('name_bn'), obj_data.get('email'), 800)

        obj_data['related_user'] = user

        super().create(obj_data)

    def update(self, obj_data):
        obj_id = obj_data.pop('id', None)
        if not obj_id:
            raise ValueError("ID is required for updating the WorkforceRepresentative")

        # Fetch the object to update
        instance = self.OBJECT_TYPE.objects.filter(pk=obj_id, is_deleted=False).first()
        if not instance:
            raise ValueError(f"WorkforceRepresentative with ID {obj_id} does not exist")

        # Update the fields of the instance
        for field, value in obj_data.items():
            setattr(instance, field, value)

        # Save the updated instance
        instance.save()

        # Log or perform any post-update actions
        logger.info(f"Updated WorkforceRepresentative with ID {obj_id}")
        return instance
