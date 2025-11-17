import os
import logging
from django.db.models import Q
from core.models import InteractiveUser
from workforce.services.workforce_sms_services import send_sms
from django.core.exceptions import ValidationError
from workforce.models import WorkforceOtp

logger = logging.getLogger(__name__)


class WorkforceOtpServices():
    OBJECT_TYPE = WorkforceOtp

    def create(self, obj_data):
        login_name = obj_data.get('nid') or obj_data.get('birth_certificate_no')
        nid = obj_data.get("nid")
        phone_number = obj_data.get("phone_number")

        if InteractiveUser.objects.filter(validity_to__isnull=True, login_name=login_name).exists():
            raise ValidationError({
                "error": "login_name already exists",
                "code": 1001,
                "message": f"User with login name '{login_name}' already exists."
            })

        if InteractiveUser.objects.filter(validity_to__isnull=True, phone=phone_number).exists():
            raise ValidationError({
                "error": "phone_number already exists",
                "code": 1002,
                "message": f"User with phone number '{phone_number}' already exists."
            })

        otp_obj = WorkforceOtp.objects.create(
            name_bn=obj_data.get("name_bn"),
            first_name_en=obj_data.get("first_name_en"),
            last_name_en=obj_data.get("last_name_en"),
            nid=nid,
            birth_certificate_no=obj_data.get("birth_certificate_no"),
            phone_number=phone_number,
            status=obj_data.get("status"),
        )

        messages = [{
            "to": otp_obj.phone_number,
            "message": f"Your verification code is {otp_obj.otp}. This code will expire in 5 minutes. Please do not share this code with anyone"
        }]
        send_sms(messages)

        return {"internal_id": otp_obj.id}

    def get(self, **kwargs):
        model = self.OBJECT_TYPE
        internal_id = kwargs.get("internal_id")
        otp = kwargs.get("otp")

        filters = []

        if internal_id and otp:
            filters.append(Q(json_ext__contains={"internal_id": internal_id}))

        queryset = model.objects.filter(*filters, status='active').only("status")

        return queryset