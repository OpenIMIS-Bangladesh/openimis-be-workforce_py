from core.gql.gql_mutations.base_mutation import BaseMutation, BaseHistoryModelCreateMutationMixin
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import gettext as _

from .apps import WorkforceConfig
from .services.workforce_organization_services import WorkforceOrganizationServices
from .gql_types import WorkforceOrganizationInputType, WorkforceRepresentativeInputType
from .services.workforce_representative_services import WorkforceRepresentativeServices

mutation_module = "workforce"


class CreateWorkforceRepresentativeMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceRepresentativeMutation"

    class Input(WorkforceRepresentativeInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        try:
            if "client_mutation_id" in data:
                data.pop('client_mutation_id')
            if "client_mutation_label" in data:
                data.pop('client_mutation_label')

            service = WorkforceRepresentativeServices(user)
            service.create(data)
            return None
        except Exception as exc:
            return [{
                'message': _("workforce.mutation.failed_to_create_workforce_organization"),
                'detail': str(exc)}
            ]


class CreateWorkforceOrganizationMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceOrganizationMutation"

    class Input(WorkforceOrganizationInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        try:
            if type(user) is AnonymousUser or not user.id:
                raise ValidationError(
                    _("mutation.authentication_required"))
            if not user.has_perms(WorkforceConfig.gql_mutation_create_workforces_perms):
                raise PermissionDenied(_("unauthorized"))

            if "client_mutation_id" in data:
                data.pop('client_mutation_id')
            if "client_mutation_label" in data:
                data.pop('client_mutation_label')

            service = WorkforceOrganizationServices(user)
            service.create(data)
            return None
        except Exception as exc:
            return [{
                'message': _("workforce.mutation.failed_to_create_workforce_organization"),
                'detail': str(exc)}
            ]
