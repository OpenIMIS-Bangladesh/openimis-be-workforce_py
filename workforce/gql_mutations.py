import graphene
from .apps import WorkforceConfig
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError, PermissionDenied
from workforce.services import update_or_create_workforce_organization
from policy import models as policy_models
from typing import Optional, List, Dict, Any
from core.schema import OpenIMISMutation
from django.utils.translation import gettext_lazy, gettext as _


class CreateWorkforceOrganizationMutation(OpenIMISMutation):
    """
    Workforce Organization
    """
    _mutation_module = "workforce"
    _mutation_class = "CreateWorkforceOrganizationMutation"

    class WorkforceOrganizationInputLabel:
        name_bn = graphene.String(required=True)
        name_en = graphene.String(required=True)
        location_id = graphene.Int(required=True)
        address = graphene.String()
        phone_number = graphene.String()
        email = graphene.String()
        website = graphene.String()
        status = graphene.Boolean()
        parent_id = graphene.Int()
        workforce_representative_id = graphene.Int(required=True)

    class Input(WorkforceOrganizationInputLabel, OpenIMISMutation.Input):
        pass

    @classmethod
    def async_mutate(cls, user, **data) -> list[dict[str, str | Any]] | None:
        try:
            if type(user) is AnonymousUser or not user.id:
                raise ValidationError(
                    _("mutation.authentication_required"))
            if not user.has_perms(WorkforceConfig.gql_mutation_create_workforces_perms):
                raise PermissionDenied(_("unauthorized"))
            client_mutation_id = data.get("client_mutation_id")
            workforce_organization = update_or_create_workforce_organization(data, user)
            CreateWorkforceOrganizationMutation.object_mutated(user, client_mutation_id=client_mutation_id, payment=workforce_organization)
            return None
        except Exception as exc:
            return [{
                'message': _("workforce.mutation.failed_to_create_workforce_organization"),
                'detail': str(exc)}
            ]
