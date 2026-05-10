import os
import logging
from django.db.models import Q
from core.models import InteractiveUser
from workforce.services.workforce_sms_services import send_sms
from django.core.exceptions import ValidationError
from workforce.models import WorkforceApplication, WorkforceUser,WorkforceEmployee
from workforce.services.helper_service import build_confirmation_link
from core.services import BaseService


logger = logging.getLogger(__name__)


class SendConfirmationLnkServices(BaseService):
    OBJECT_TYPE = WorkforceApplication

    def create(self, obj_data):
        application_id = obj_data.get('id')
        application_instance = WorkforceApplication.objects.get(id=application_id)
        workforce_employee = WorkforceEmployee.objects.get(
            id=application_instance.workforce_employee.id)
        phone_number = workforce_employee.phone_number

        # sending message to user
        link = build_confirmation_link(application_id)
        message = f"Please confirm receipt: {link}"
        send_sms(phone_number, message)

        # if os.environ.get("TEST_SIGNUP_OTP"):
        #     otp = os.environ.get("TEST_SIGNUP_OTP")
        # else:
        #     otp = None
        #
        #
        # if otp:
        #     otp_obj = WorkforceOtp.objects.create(
        #         name_bn=obj_data.get("name_bn"),
        #         first_name_en=obj_data.get("first_name_en"),
        #         last_name_en=obj_data.get("last_name_en"),
        #         nid=nid,
        #         birth_certificate_no=obj_data.get("birth_certificate_no"),
        #         phone_number=phone_number,
        #         otp=otp,
        #         status=obj_data.get("status"),
        #     )
        # else:
        #     otp_obj = WorkforceOtp.objects.create(
        #         name_bn=obj_data.get("name_bn"),
        #         first_name_en=obj_data.get("first_name_en"),
        #         last_name_en=obj_data.get("last_name_en"),
        #         nid=nid,
        #         birth_certificate_no=obj_data.get("birth_certificate_no"),
        #         phone_number=phone_number,
        #         status=obj_data.get("status"),
        #     )
        #
        # otp_instance = WorkforceOtp.objects.get(id=otp_obj.id)
        #
        # if otp_instance:
        #     message = f"Your verification code is {otp_instance.otp}. This code will expire in 5 minutes. Please do not share this code with anyone."
        #     send_sms(sms_to=otp_obj.phone_number, message=message)
        # else:
        #     # raise ValidationError({
        #     #     "error": "failed_to_create_otp",
        #     #     "code": 1005,
        #     #     "message": f"OTP creation failed due to an unknown error"
        #     # })
        #     return {
        #         "error": "failed_to_create_otp",
        #         "code": 1005,
        #         "message": f"OTP creation failed due to an unknown error"
        #     }
        # return {"internal_id": otp_obj.id}
