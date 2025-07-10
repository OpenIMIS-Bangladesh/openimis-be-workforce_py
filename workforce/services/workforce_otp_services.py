import os
from dotenv import load_dotenv
import logging
from django.db.models import Q
from django.utils import timezone
from sms_services import send_bulk_sms
from workforce.models import WorkforceOtp

load_dotenv()
logger = logging.getLogger(__name__)
BULKSMS_API_KEY = os.getenv("BULKSMS_API_KEY")


class WorkforceOtpServices():
    OBJECT_TYPE = WorkforceOtp

    def create(self, obj_data):

        otp_obj = WorkforceOtp.objects.create(
            name_bn=obj_data.get("name_bn"),
            first_name_en=obj_data.get("first_name_en"),
            last_name_en=obj_data.get("last_name_en"),
            nid=obj_data.get("nid"),
            birth_certificate_no=obj_data.get("birth_certificate_no"),
            phone_number=obj_data.get("phone_number"),
            status=obj_data.get("status"),
        )
        print(f"==========================> otp {otp_obj.otp}")
        message = f"Your verification code is {otp_obj.otp}. This code will expire in 5 minutes. Please do not share this code with anyone"

        send_bulk_sms(BULKSMS_API_KEY, otp_obj.phone_number, message)

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