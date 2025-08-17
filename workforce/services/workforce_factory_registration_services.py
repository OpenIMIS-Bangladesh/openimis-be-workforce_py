import logging
import uuid
from django.db.models import Q
from django.utils.dateparse import parse_date
from workforce.models import WorkforceFactoryRegistration

logger = logging.getLogger(__name__)


class WorkforceFactoryRegistrationServices:
    OBJECT_TYPE = WorkforceFactoryRegistration

    CAMEL_TO_SNAKE = {
        # root factory fields
        'workforceEmployerId': 'workforce_employer_id',
        'employerId': 'employer_id',
        'employerIdLima': 'employer_id_lima',
        'nameBn': 'name_bn',
        'nameEn': 'name_en',
        'locationId': 'location_id',
        'phoneNumber': 'phone_number',
        'associationType': 'association_type',
        'isSameCompanyRepresentative': 'is_same_company_representative',
        'status': 'status',
        # representative fields
        'representativeType': 'representative_type',
        'representativeNameBn': 'representative_name_bn',
        'representativeNameEn': 'representative_name_en',
        'representativeLocationId': 'representative_location_id',
        'representativeAddress': 'representative_address',
        'representativePhoneNumber': 'representative_phone_number',
        'representativeEmail': 'representative_email',
        'representativeNid': 'representative_nid',
        'representativePassportNo': 'representative_passport_no',
        'representativeBirthDate': 'representative_birth_date',
        'representativePosition': 'representative_position',
        'representativeStatus': 'representative_status',
    }

    DATE_FIELDS = {"representative_birth_date"}

    def get(self, **kwargs):
        filters = []
        model = self.OBJECT_TYPE
        client_mutation_id = kwargs.get("client_mutation_id")
        if client_mutation_id:
            filters.append(Q(json_ext__contains={"client_mutation_id": client_mutation_id}))
        return model.objects.filter(*filters, is_deleted=False).all()

    def _normalize(self, obj_data):
        if not isinstance(obj_data, dict):
            return {}
        normalized = {}
        for k, v in obj_data.items():
            target = self.CAMEL_TO_SNAKE.get(k, k)
            normalized[target] = v
        # convert date strings
        for f in self.DATE_FIELDS:
            if f in normalized and isinstance(normalized[f], str) and normalized[f]:
                parsed = parse_date(normalized[f])
                if parsed:
                    normalized[f] = parsed
        return normalized

    def create(self, obj_data):
        try:
            data = self._normalize(obj_data)
            data.pop("json_ext", None)
            data['id'] = data.get('id') or data.get('uuid') or uuid.uuid4()
            data['factory_id'] = data.get('factory_id') or None
            obj = self.OBJECT_TYPE.objects.create(**data)
            return {"success": True, "data": {"id": str(obj.id)}}
        except Exception as e:
            logger.error(f"Error creating WorkforceFactoryRegistration: {e}")
            return {"success": False, "error": str(e)}

    def update(self, obj_data):
        data = self._normalize(obj_data)
        obj_id = data.get('id') or data.get('uuid')
        if not obj_id:
            return [{"message": "Missing id for update", "detail": "Provide 'id'"}]
        obj = self.OBJECT_TYPE.objects.filter(id=obj_id).first()
        if not obj:
            return [{"message": "Object not found", "detail": str(obj_id)}]
        for k, v in data.items():
            if k in ['id', 'uuid']:
                continue
            setattr(obj, k, v)
        obj.save()
        return {"success": True, "data": {"id": str(obj.id)}}
