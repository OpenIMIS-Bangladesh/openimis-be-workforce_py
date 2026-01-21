import os
import logging
from django.db.models import Q
from core.models import InteractiveUser
from workforce.services.workforce_sms_services import send_sms
from django.core.exceptions import ValidationError
from workforce.models import WorkforceOtp, WorkforceUser

logger = logging.getLogger(__name__)


class WorkforceOtpServices():
    OBJECT_TYPE = WorkforceOtp

    def create(self, obj_data):
        login_name = obj_data.get('nid') or obj_data.get('birth_certificate_no')
        nid = obj_data.get("nid")
        phone_number = obj_data.get("phone_number")
        if os.environ.get("TEST_SIGNUP_OTP"):
            otp = os.environ.get("TEST_SIGNUP_OTP")
        else:
            otp=None

        if InteractiveUser.objects.filter(validity_to__isnull=True, login_name=login_name).exists():
            # raise ValidationError({
            #     "error": "login_name_already_exists   ",
            #     "code": 1001,
            #     "message": f"User with login name '{login_name}' already exists."
            # })
            return {
                "error": "login_name_already_exists ",
                "code": 1001,
                "message": f"User with login name '{login_name}' already exists."
            }

        if WorkforceUser.objects.filter(nid=nid).exists():
            # raise ValidationError({
            #     "error": "duplicate_nid",
            #     "code": 1003,
            #     "message": f"Duplicate NID '{nid}' in workforce_user."
            # })
            return  {
                "error": "duplicate_nid",
                "code": 1003,
                "message": f"Duplicate NID '{nid}' in workforce_user."
            }

        if InteractiveUser.objects.filter(validity_to__isnull=True, phone=phone_number).exists():
            # raise ValidationError({
            #     "error": "phone_number_already_exists",
            #     "code": 1002,
            #     "message": f"User with phone number '{phone_number}' already exists."
            # })
            return {
                "error": "phone_number_already_exists",
                "code": 1002,
                "message": f"User with phone number '{phone_number}' already exists."
            }

        if WorkforceUser.objects.filter(phone_number=phone_number).exists():
            # raise ValidationError({
            #     "error": "duplicate_phone_number",
            #     "code": 1004,
            #     "message": f"Duplicate phone '{phone_number}' in workforce_user."
            # })
            return {
                "error": "duplicate_phone_number",
                "code": 1004,
                "message": f"Duplicate phone '{phone_number}' in workforce_user."
            }

        if otp:
            otp_obj = WorkforceOtp.objects.create(
                name_bn=obj_data.get("name_bn"),
                first_name_en=obj_data.get("first_name_en"),
                last_name_en=obj_data.get("last_name_en"),
                nid=nid,
                birth_certificate_no=obj_data.get("birth_certificate_no"),
                phone_number=phone_number,
                otp=otp,
                status=obj_data.get("status"),
            )
        else:
            otp_obj = WorkforceOtp.objects.create(
                name_bn=obj_data.get("name_bn"),
                first_name_en=obj_data.get("first_name_en"),
                last_name_en=obj_data.get("last_name_en"),
                nid=nid,
                birth_certificate_no=obj_data.get("birth_certificate_no"),
                phone_number=phone_number,
                status=obj_data.get("status"),
            )

        otp_instance = WorkforceOtp.objects.get(id=otp_obj.id)

        if otp_instance:
            message = f"Your verification code is {otp_instance.otp}. This code will expire in 5 minutes. Please do not share this code with anyone."
            send_sms(sms_to=otp_obj.phone_number, message=message)
        else:
            # raise ValidationError({
            #     "error": "failed_to_create_otp",
            #     "code": 1005,
            #     "message": f"OTP creation failed due to an unknown error"
            # })
            return  {
                "error": "failed_to_create_otp",
                "code": 1005,
                "message": f"OTP creation failed due to an unknown error"
            }
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