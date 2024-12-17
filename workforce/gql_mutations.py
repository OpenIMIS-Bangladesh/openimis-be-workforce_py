from core.gql.gql_mutations.base_mutation import BaseMutation, BaseHistoryModelCreateMutationMixin
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import gettext as _
from .apps import WorkforceConfig
from .gql_types import (
    WorkforceOrganizationInputType, WorkforceRepresentativeInputType, WorkforceOrganizationUnitInputType,
    WorkforceOrganizationUnitDesignationInputType
)
from .services.workforce_organization_services import WorkforceOrganizationServices
from .services.workforce_representative_services import WorkforceRepresentativeServices
from .services.workforce_organization_unit_services import WorkforceOrganizationUnitServices
from .services.workforce_organization_unit_designation_services import WorkforceOrganizationUnitDesignationServices

mutation_module = "workforce"


def auth_permission_validation(failure_message, required_permission, service_instance, user, data):
    """
    Validates user authentication and permissions, processes data, and calls the service method.

    :param failure_message: Error message to return on failure.
    :param required_permission: Permissions required for the action.
    :param service_instance: Instance of the service to call.
    :param user: User performing the action.
    :param data: Data to process.
    :return: None or an error dictionary.
    """
    try:
        if isinstance(user, AnonymousUser) or not user.id:
            raise ValidationError(_("mutation.authentication_required"))

        if not user.has_perms(required_permission):
            raise PermissionDenied(_("unauthorized"))

        processed_data = {k: v for k, v in data.items() if k not in ["client_mutation_id", "client_mutation_label"]}

        service_instance.create(processed_data)
        return None
    except Exception as exc:
        return [{
            'message': _(failure_message),
            'detail': str(exc)
        }]


class CreateWorkforceRepresentativeMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceRepresentativeMutation"

    class Input(WorkforceRepresentativeInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_representative"
        required_permission = WorkforceConfig.gql_mutation_create_workforces_perms
        service_instance = WorkforceRepresentativeServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceOrganizationMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceOrganizationMutation"

    class Input(WorkforceOrganizationInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_organization"
        required_permission = WorkforceConfig.gql_mutation_create_workforces_perms
        service_instance = WorkforceOrganizationServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceOrganizationUnitMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceOrganizationUnitMutation"

    class Input(WorkforceOrganizationUnitInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_organization_unit"
        required_permission = WorkforceConfig.gql_mutation_create_workforces_perms
        service_instance = WorkforceOrganizationUnitServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceOrganizationUnitDesignationMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceOrganizationUnitDesignationMutation"

    class Input(WorkforceOrganizationUnitDesignationInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_organization_unit_designation"
        required_permission = WorkforceConfig.gql_mutation_create_workforces_perms
        service_instance = WorkforceOrganizationUnitDesignationServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result
