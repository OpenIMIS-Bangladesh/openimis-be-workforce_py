import logging
import uuid
import json
import base64
from core.services import BaseService
from workforce.models import WebsiteLegalGuideline

logger = logging.getLogger(__name__)

def extract_uuid(encoded_str):
    decoded = base64.b64decode(encoded_str).decode()
    return decoded.split(":")[1]

class WebsiteLegalGuidelineServices(BaseService):
    OBJECT_TYPE = WebsiteLegalGuideline

    def create(self, obj_data):
        return super().create(obj_data)
    def update(self, obj_data):
        return super().update(obj_data)
