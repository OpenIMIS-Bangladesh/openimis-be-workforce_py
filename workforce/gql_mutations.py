from core.gql.gql_mutations.base_mutation import BaseMutation, BaseHistoryModelCreateMutationMixin
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import gettext as _
from .apps import WorkforceConfig
import graphene
from .gql_types import (
    WorkforceOrganizationInputType, WorkforceRepresentativeInputType, WorkforceOrganizationUnitInputType,
    WorkforceOrganizationUnitDesignationInputType, WorkforceOrganizationEmployeeInputType,
    WorkforceEmployerInputType, WorkforceOfficeInputType, WorkforceFactoryInputType,
    WorkforceEmployeeInputType, WorkforceOrganizationEmployeeDesignationInputType,
    WorkforceEmployerStatusInput, WorkforceDocumentInputType, BankInputType,
    WorkforceEmployeeDependentInputType
)
from .services.workforce_organization_services import WorkforceOrganizationServices
from .services.workforce_representative_services import WorkforceRepresentativeServices
from .services.workforce_organization_unit_services import WorkforceOrganizationUnitServices
from .services.workforce_organization_unit_designation_services import WorkforceOrganizationUnitDesignationServices
from .services.workforce_organization_employee_services import WorkforceOrganizationEmployeeServices
from .services.workforce_employer_services import WorkforceEmployerServices
from .services.workforce_office_services import WorkforceOfficeServices
from .services.workforce_factory_services import WorkforceFactoryServices
from .services.workforce_employee_services import WorkforceEmployeeServices
from .services.workforce_organization_employee_designation_services import WorkforceOrganizationEmployeeDesignationServices
from .services.workforce_document_services import WorkforceDocumentServices
from .services.bank_services import BankServices
from .services.workforce_employee_dependent_services import WorkforceEmployeeDependentServices

mutation_module = "workforce"


def auth_permission_validation(failure_message, required_permission, call_type, service_instance, user, data):
    """
    Validates user authentication and permissions, processes data, and calls the service method.

    :param failure_message: Error message to return on failure.
    :param required_permission: Permissions required for the action.
    :param call_type: Type of function to call.
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
        if data.get('client_mutation_id') and data.get('client_mutation_id') != '':
            processed_data['json_ext'] = {'client_mutation_id': data.get('client_mutation_id')}

        if call_type == 'create':
            return service_instance.create(processed_data)
        if call_type == 'update':
            return service_instance.update(processed_data)
        if call_type == 'update_status':
            return service_instance.update_status(processed_data)
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
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceRepresentativeServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceRepresentativeMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceRepresentativeMutation"

    class Input(WorkforceRepresentativeInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_representative"
        required_permission = WorkforceConfig.gql_mutation_update_workforces_perms
        service_instance = WorkforceRepresentativeServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
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
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceOrganizationServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceOrganizationMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceOrganizationMutation"

    class Input(WorkforceOrganizationInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_organization"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceOrganizationServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
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
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceOrganizationUnitServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceOrganizationUnitMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceOrganizationUnitMutation"

    class Input(WorkforceOrganizationUnitInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_organization_unit"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceOrganizationUnitServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
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
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceOrganizationUnitDesignationServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceOrganizationUnitDesignationMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceOrganizationUnitDesignationMutation"

    class Input(WorkforceOrganizationUnitDesignationInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_organization_unit_designation"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceOrganizationUnitDesignationServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceOrganizationEmployeeMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceOrganizationEmployeeMutation"

    class Input(WorkforceOrganizationEmployeeInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_organization_employee"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceOrganizationEmployeeServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceOrganizationEmployeeMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceOrganizationEmployeeMutation"

    class Input(WorkforceOrganizationEmployeeInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_organization_employee"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceOrganizationEmployeeServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceOrganizationEmployeeDesignationMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceOrganizationEmployeeDesignationMutation"

    class Input(WorkforceOrganizationEmployeeDesignationInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_organization_employee_designation"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceOrganizationEmployeeDesignationServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceOrganizationEmployeeDesignationMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceOrganizationEmployeeDesignationMutation"

    class Input(WorkforceOrganizationEmployeeDesignationInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_organization_employee_designation"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceOrganizationEmployeeDesignationServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceEmployerMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceEmployerMutation"

    class Input(WorkforceEmployerInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_employer"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceEmployerServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceEmployerMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceEmployerMutation"

    class Input(WorkforceEmployerInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_employer"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceEmployerServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceEmployerStatusMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceEmployerStatusMutation"

    class Input(WorkforceEmployerStatusInput):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_employer_status"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceEmployerServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update_status',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceOfficeMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceOfficeMutation"

    class Input(WorkforceOfficeInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_office"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceOfficeServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceOfficeMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceOfficeMutation"

    class Input(WorkforceOfficeInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_office"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceOfficeServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceFactoryMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceFactoryMutation"

    class Input(WorkforceFactoryInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_factory"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceFactoryServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceFactoryMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceFactoryMutation"

    class Input(WorkforceFactoryInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_factory"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceFactoryServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceEmployeeMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceEmployeeMutation"

    class Input(WorkforceEmployeeInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_employee"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceEmployeeServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceEmployeeMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceEmployeeMutation"

    class Input(WorkforceEmployeeInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_employee"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceEmployeeServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceDocumentMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceDocumentMutation"

    class Input(WorkforceDocumentInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_document"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceDocumentServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceDocumentMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceDocumentsMutation"

    class Input(WorkforceDocumentInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_document"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceDocumentServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateBankMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateBankMutation"

    class Input(BankInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_bank"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = BankServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateBankMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateBankMutation"

    class Input(BankInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_bank"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = BankServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceEmployeeDependentMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceEmployeeDependentMutation"

    class Input(WorkforceEmployeeDependentInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_employee_dependent"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceEmployeeDependentServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceEmployeeDependentMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceEmployeeDependentMutation"

    class Input(WorkforceEmployeeDependentInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_employee_dependent"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceEmployeeDependentServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result