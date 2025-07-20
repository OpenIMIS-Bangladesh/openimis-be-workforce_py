from core.services.userServices import create_or_update_interactive_user
import logging
import uuid
from django.db.models import Q

from workforce.models import WorkforceUser
from workforce.services.workforce_employee_services import WorkforceEmployeeServices
from core.models import User

logger = logging.getLogger(__name__)


class WorkforceUserServices():
    OBJECT_TYPE = WorkforceUser

    def create(self, obj_data):
        login_name = obj_data.get('nid') or obj_data.get('birth_certificate_no')
        data = {
            "username": login_name,
            "other_names": ' ',
            "last_name": obj_data.get('last_name_en'),
            "phone": obj_data.get('phone_number'),
            "email": '',
            "language": 'en',
            "health_facility_id": 1,
            "password": obj_data.get('password'),
            "roles": obj_data.get("roles", []),
        }

        created_user = create_or_update_interactive_user(None, data, 1, False)
        create_user_id = created_user[0].id

        user_obj = WorkforceUser.objects.create(
            name_bn=obj_data.get("name_bn"),
            first_name_en=obj_data.get("first_name_en"),
            last_name_en=obj_data.get("last_name_en"),
            nid=obj_data.get("nid"),
            phone_number=obj_data.get("phone_number"),
            status=obj_data.get("status"),
        )

        user = User.objects.get(i_user=1)

        employee_service = WorkforceEmployeeServices(user)
        employee_data = {
            "first_name_bn": obj_data.get("name_bn"),
            "last_name_bn": "",
            "first_name_en": obj_data.get("first_name_en"),
            "last_name_en": "",
            "nid": obj_data.get("nid"),
            "phone_number": obj_data.get("phone_number"),
            "birth_certificate_no": obj_data.get('birth_certificate_no'),
            "related_user_id": create_user_id,
        }
        employee_create = employee_service.create(employee_data)

        return {"internal_id": str(uuid.uuid4())}

    def update(self, obj_data):
        data = {
            "username": obj_data.get('nid'),
            "other_names": ' ',
            "last_name": obj_data.get('last_name_en'),
            "phone": obj_data.get('phone_number'),
            "email": '',
            "language": 'en',
            "health_facility_id": 1,
            "password": obj_data.get('password'),
            "roles": obj_data.get("roles", []),
        }

        create_or_update_interactive_user(None, data, 1, False)

    def get(self, **kwargs):
        filters = []
        model = self.OBJECT_TYPE

        client_mutation_id = kwargs.get("client_mutation_id", None)
        if client_mutation_id:
            filters.append(
                Q(json_ext__contains={"client_mutation_id": client_mutation_id}))

        query = model.objects.filter(*filters, status='active').all()
        return query
