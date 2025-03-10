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
    WorkforceEmployeeDependentInputType, WorkforceEmployeeDesignationInputType,
    WorkforceEmployeeAccidentInputType, WorkforceEmployeeAccountInfoInputType,
    WorkforceApplicationInputType,
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
from .services.workforce_organization_employee_designation_services import \
    WorkforceOrganizationEmployeeDesignationServices
from .services.workforce_document_services import WorkforceDocumentServices
from .services.bank_services import BankServices
from .services.workforce_employee_dependent_services import WorkforceEmployeeDependentServices
from .services.workforce_employee_designation_services import WorkforceEmployeeDesignationServices
from .services.workforce_employee_accident_services import WorkforceEmployeeAccidentServices
from .services.workforce_employee_account_info_services import WorkforceEmployeeAccountInfoServices
from .services.workforce_temporary_application_services import WorkforceTemporaryApplicationServices

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
        required_permission = WorkforceConfig.gql_query_workforces_perms
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
        workforce_employer_id = graphene.UUID()
        workforce_factory_id = graphene.UUID()
        join_date = graphene.Date()
        position = graphene.String()
        monthly_earning = graphene.String()
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_employee"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceEmployeeServices(user)

        workforce_employer_id = data.pop('workforce_employer_id')
        workforce_factory_id = data.pop('workforce_factory_id')
        join_date = data.pop('join_date')
        position = data.pop('position')
        monthly_earning = data.pop('monthly_earning')

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        if result and isinstance(result, dict):
            # Check success flag
            if result.get("success") is True:  # Ensure success is True
                # Get the "data" field from result
                created_obj = result.get("data")

                if created_obj:  # Ensure created_obj is not None or empty
                    # Extract values with default fallback if necessary
                    employee_designation_service = WorkforceEmployeeDesignationServices(user)

                    employee_designation_obj = {
                        "workforce_employee_id": created_obj.get('id', None),  # Safely get 'id', default to None if missing
                        "workforce_company_id": workforce_employer_id,
                        "workforce_factory_id": workforce_factory_id,
                        "join_date": join_date,
                        "monthly_salary": monthly_earning,  # Safely get 'monthly_earning'
                        "position": position,  # Safely get 'position'
                    }

                    # Proceed with creating the employee designation
                    d_created_obj = employee_designation_service.create(employee_designation_obj)

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


class CreateWorkforceEmployeeDesignationMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceEmployeeDesignationMutation"

    class Input(WorkforceEmployeeDesignationInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_employee_designation"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceEmployeeDesignationServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceEmployeeDesignationMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceEmployeeDesignationMutation"

    class Input(WorkforceEmployeeDesignationInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_employee_designation"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceEmployeeDesignationServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceEmployeeAccidentMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceEmployeeAccidentMutation"

    class Input(WorkforceEmployeeAccidentInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_employee_accident"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceEmployeeAccidentServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceEmployeeAccidentMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceEmployeeAccidentMutation"

    class Input(WorkforceEmployeeAccidentInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_employee_designation"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceEmployeeAccidentServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceEmployeeAccountInfoMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceEmployeeAccountInfoMutation"

    class Input(WorkforceEmployeeAccountInfoInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_employee_account_info"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceEmployeeAccountInfoServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceEmployeeAccountInfoMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceEmployeeAccountInfoMutation"

    class Input(WorkforceEmployeeAccountInfoInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_employee_account_info"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceEmployeeAccountInfoServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceTemporaryApplicationMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceTemporaryApplicationMutation"

    class Input(WorkforceApplicationInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_temporary_application"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceTemporaryApplicationServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceTemporaryApplicationMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceTemporaryApplicationMutation"

    class Input(WorkforceApplicationInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_temporary_application"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceTemporaryApplicationServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result
