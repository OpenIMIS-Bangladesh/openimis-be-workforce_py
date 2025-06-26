import logging
import random
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from core.services import BaseService
from workforce.models import WorkforceApplication, WorkforceGrantMoney
from django.db.models import Q

logger = logging.getLogger(__name__)


class WorkforceApplicationServices(BaseService):
    OBJECT_TYPE = WorkforceApplication

    def get(self, **kwargs):
        filters = []
        model = self.OBJECT_TYPE

        client_mutation_id = kwargs.get("client_mutation_id", None)
        if client_mutation_id:
            filters.append(Q(json_ext__contains={"client_mutation_id": client_mutation_id}))

        query = model.objects.filter(*filters, is_deleted=False).all()
        return query

    def create(self, obj_data):
        phone_number = obj_data.get("phone_number")
        application_type = obj_data.get("application_type")
        organization_type = obj_data.get("organization_type")

        if phone_number:
            tracking_number = phone_number + str(random.randint(0,99)).zfill(2)
            obj_data["tracking_number"] = tracking_number

        if application_type and organization_type:
            try:
                grant = WorkforceGrantMoney.objects.get(
                    application_type=application_type,
                    organization_type=organization_type
                )

                obj_data["grant_money_id"] = grant.id

            except ObjectDoesNotExist:
                logger.warning(
                    "No matching WorkforceGrantMoney found for given application_type and organization_type.")
            except MultipleObjectsReturned:
                logger.error("Multiple WorkforceGrantMoney entries found. Expected only one.")
                raise

        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)
