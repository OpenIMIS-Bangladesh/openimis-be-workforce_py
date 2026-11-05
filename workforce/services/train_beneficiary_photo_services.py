import os
import logging
from django.db.models import Q
from core.models import InteractiveUser
from workforce.services.workforce_sms_services import send_sms
from django.core.exceptions import ValidationError
from workforce.models import WorkforceDocument, WorkforceUser,WorkforceEmployee
from workforce.services.helper_service import build_confirmation_link
from core.services import BaseService
from django.core.files.storage import default_storage


logger = logging.getLogger(__name__)


class TrainBeneficiaryPhotoServices():
    OBJECT_TYPE = WorkforceDocument

    def create(self, obj_data =None):
        document_instance = WorkforceDocument.objects.all()
        for document in document_instance:
            # --- NEW BIOMETRIC INTEGRATION ---
            # Ensure we only process photos linked to the dependent
            PHOTO_TYPES = {
                "nominee's photo",
                "nominee photo",
                "employee photo",
                "workers photo",
                "photo of worker",
            }
            if document.document_type in PHOTO_TYPES and document.path:
                try:
                    path = document.path
                    if 'file_storage' in path:
                        filename = path.replace("/file_storage/content/workforce/", "")
                    else:
                        filename = path.replace("/content/workforce/", "")
                    file_path = os.path.join('content', 'workforce', filename)
                    if not default_storage.exists(file_path):
                        continue
                    file = default_storage.open(file_path)
                    image_bytes = file.read()
                    # Add this with your other imports at the top
                    from biometric_verification.services import BiometricService
                    # Use the new method that accepts raw bytes and document id
                    result = BiometricService.compute_embedding_from_bytes(
                        document_id=document.id,
                        image_bytes=image_bytes
                    )
                    if result.success:
                        logger.info(
                            f"Generated biometric embedding for dependent {document.id}")
                    else:
                        logger.error(
                            f"Failed to generate embedding for dependent {document.id}: {result.error}")
                except Exception as e:
                    logger.error(
                        f"Failed to generate embedding for dependent {document.id}: {e}")
            # ---------------------------------

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
