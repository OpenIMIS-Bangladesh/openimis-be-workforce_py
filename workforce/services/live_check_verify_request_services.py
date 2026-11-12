import os
import logging
from datetime import date
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from core.services import BaseService
from core.models import User
from workforce.models import (
    WorkforceDocument,
    WorkforceLiveCheckRequest,
    WorkforceEisPaymentProcess,
    WorkforceEmployeeDependent,
    WorkforceApplication,
)
from workforce.services.workforce_document_services import WorkforceDocumentServices

logger = logging.getLogger(__name__)


class LiveCheckVerifyRequestServices(BaseService):
    OBJECT_TYPE = WorkforceLiveCheckRequest

    def update(self, obj_data: dict):
        """
        1. Searches the document from the documents table using document_id (or id).
        2. Updates the document row via WorkforceDocumentServices.
        3. Creates a new WorkforceLiveCheckRequest record populated from that document.
        """
        doc_id = (
            obj_data.get("document_id")
            or obj_data.get("workforce_document_id")
            or obj_data.get("id")
        )

        if not doc_id:
            raise ValidationError(_("document_id or id is required."))

        with transaction.atomic():
            # 1. Search that row from documents table
            document = WorkforceDocument.objects.filter(id=doc_id, is_deleted=False).first()
            if not document:
                raise ValidationError(_(f"WorkforceDocument with id '{doc_id}' not found."))

            # 2. Update the document row using WorkforceDocumentServices
            doc_service = WorkforceDocumentServices(self.user)
            doc_payload = {
                "id": str(document.id),
                "path": obj_data.get("path") or document.path,
                "url": obj_data.get("url") or document.url,
                "is_verify_request": obj_data.get("is_verify_request", True),
                "verify_request_reason": obj_data.get("verify_request_reason") or obj_data.get("reason"),
                "status": obj_data.get("status") or document.status,
            }
            cleaned_doc_payload = {k: v for k, v in doc_payload.items() if v not in ("", None, "undefined")}
            doc_service.update(cleaned_doc_payload)
            document.refresh_from_db()

            # 3. Pull details from document & related models
            application = document.workforce_application
            dependent = document.workforce_dependent
            summary = document.application_summary

            beneficiary_name_en = obj_data.get("beneficiary_name_en")
            beneficiary_name_bn = obj_data.get("beneficiary_name_bn")
            phone_number = obj_data.get("phone_number")
            beneficiary_id = obj_data.get("beneficiary_id")

            # Fallback to dependent details if available
            if dependent:
                beneficiary_name_en = beneficiary_name_en or dependent.name_en
                beneficiary_name_bn = beneficiary_name_bn or dependent.name_bn
                phone_number = phone_number or dependent.phone_number

            # Fallback to payment process to find beneficiary_id
            if not beneficiary_id and application:
                payment_process = WorkforceEisPaymentProcess.objects.filter(
                    workforce_application=application,
                    is_deleted=False,
                )
                if dependent:
                    payment_process = payment_process.filter(workforce_employee_dependent=dependent)
                payment_record = payment_process.first()
                if payment_record:
                    beneficiary_id = payment_record.beneficiary_id
                    phone_number = phone_number or payment_record.phone_number

            # 4. Create a row in the WorkforceLiveCheckRequest table
            live_check = WorkforceLiveCheckRequest(
                workforce_application=application,
                workforce_application_summary=summary,
                workforce_employee_dependent=dependent,
                workforce_document=document,
                processing_date=obj_data.get("processing_date") or date.today(),
                is_approved=obj_data.get("is_approved", False),
                approval_date=obj_data.get("approval_date"),
                beneficiary_id=beneficiary_id,
                beneficiary_name_en=beneficiary_name_en,
                beneficiary_name_bn=beneficiary_name_bn,
                phone_number=phone_number,
                status=obj_data.get("status", "pending"),
                reason=obj_data.get("reason") or obj_data.get("verify_request_reason"),
                remarks=obj_data.get("remarks"),
            )
            live_check.save(user=self.user, username=getattr(self.user, "username", None))

            return {
                "success": True,
                "message": "Live check verification request created successfully",
                "data": {
                    "id": str(live_check.id),
                    "document_id": str(document.id),
                    "workforce_application_id": str(application.id) if application else None,
                    "workforce_dependent_id": str(dependent.id) if dependent else None,
                    "beneficiary_id": beneficiary_id,
                },
            }

    def create(self, obj_data: dict):
        return self.update(obj_data)