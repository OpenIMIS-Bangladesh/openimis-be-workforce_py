import logging
from django.db.models import Q
from gettext import gettext as _
from workforce.apps import WorkforceConfig
from .models import (
    WorkforceRepresentative, WorkforceOrganization, WorkforceOrganizationUnit,
    WorkforceOrganizationUnitDesignation, WorkforceOrganizationEmployee,
    WorkforceEmployer, WorkforceOffice, WorkforceFactory, WorkforceEmployee
)

logger = logging.getLogger(__file__)


def update_or_create_workforce_organization(data, user):
    if "client_mutation_id" in data:
        data.pop('client_mutation_id')
    if "client_mutation_label" in data:
        data.pop('client_mutation_label')
    from core import datetime
    now = datetime.datetime.now()
    data['validity_from'] = now
    workforce_id = data.pop("id") if "id" in data else None
    if workforce_id:
        workforce_organization = WorkforceOrganization.objects.get(id=workforce_id)
        workforce_organization.save_history()
        [setattr(workforce_organization, k, v) for k, v in data.items()]
        workforce_organization.save()
    else:
        workforce_organization = WorkforceOrganization.objects.create(**data)
    return workforce_organization
