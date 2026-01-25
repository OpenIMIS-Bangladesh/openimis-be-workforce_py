from core.gql.gql_mutations.base_mutation import BaseMutation, BaseHistoryModelCreateMutationMixin
from graphql_jwt.mutations import JSONWebTokenMutation, mixins
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import gettext as _
import base64
from core.models import InteractiveUser
from core.schema import OpenIMISMutation
from .apps import WorkforceConfig
from datetime import date, datetime
import json
import graphene
from .gql_types import (
    WorkforceOrganizationInputType, WorkforceRepresentativeInputType, WorkforceOrganizationUnitInputType,
    WorkforceOrganizationUnitDesignationInputType, WorkforceOrganizationEmployeeInputType,
    WorkforceEmployerInputType, WorkforceOfficeInputType, WorkforceFactoryInputType,
    WorkforceEmployeeInputType, WorkforceOrganizationEmployeeDesignationInputType,
    WorkforceEmployerStatusInput, WorkforceDocumentInputType, WorkforceBankInputType,
    WorkforceEmployeeDependentInputType, WorkforceEmployeeDesignationInputType,
    WorkforceEmployeeAccidentInputType, WorkforceEmployeeAccountInfoInputType,
    WorkforceApplicationInputType, WorkforceDocumentTypeInputType, WorkforceDocumentMapInputType,
    WorkforceUserInputType, WorkforceApplicationMovementInputType, WorkforceApplicationSummaryInputType,
    WorkforceApplicationSummaryMovementInputType, WorkforceGrantMoneyInputType, WorkforceDiseasesInputType,
    WorkforceEducationInputType, WorkforceEmployeeBankingInfoInputType,
    WorkforceFactoryRegistrationInputType,
    WorkforceFactoryRegistrationApprovalInputType, WorkforceApplicationBulkUpdateInputType,
    WorkforceInteractiveUserInputType, WorkforceAllAssociationInputType, WorkforceOtherCompensationInfoInputType
)

from .models import Bank
from .services.workforce_organization_services import WorkforceOrganizationServices
from .services.workforce_other_compensation_info_services import WorkforceOtherCompensationInfoServices
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
from .services.workforce_application_services import WorkforceApplicationServices
from .services.workforce_document_type_services import WorkforceDocumentTypeServices
from .services.workforce_document_map_services import WorkforceDocumentMapServices
from .services.workforce_user_services import WorkforceUserServices
from .services.workforce_otp_services import WorkforceOtpServices
from .services.workforce_application_movement_services import WorkforceApplicationMovementServices
from .services.workforce_application_summary_services import WorkforceApplicationSummaryServices
from .services.workforce_application_summary_movement_services import WorkforceApplicationSummaryMovementServices
from .services.workforce_grant_money_services import WorkforceGrantMoneyServices
from .services.workforce_diseases_services import WorkforceDiseasesServices
from .services.workforce_education_services import WorkforceEducationServices
from .services.workforce_employee_banking_info_services import WorkforceEmployeeBankingInfoServices
from .services.workforce_factory_registration_services import WorkforceFactoryRegistrationServices
from .services.workforce_factory_registration_services import WorkforceFactoryRegistrationServices
from .services.workforce_application_bulk_movement_services import WorkforceApplicationBulkMovementServices
from .services.update_interactive_user_services import UpdateInteractiveUserServices
from .services.workforce_all_association_services import WorkforceAllAssociationServices
from .gql_queries import (
    WorkforceInteractiveUserGQLType
)
from .services.helper_service import generate_beneficiary_id
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

        processed_data = {k: v for k, v in data.items() if k not in [
            "client_mutation_id", "client_mutation_label"]}
        if data.get('client_mutation_id') and data.get('client_mutation_id') != '':
            processed_data['json_ext'] = {
                'client_mutation_id': data.get('client_mutation_id')}

        if call_type == 'create':
            return service_instance.create(processed_data)
        if call_type == 'update':
            return service_instance.update(processed_data)
        if call_type == 'update_status':
            return service_instance.update_status(processed_data)
        if call_type == 'approve':
            return service_instance.approve(processed_data)
        if call_type == 'bulk_forward_to_doctors':
            return service_instance.bulk_forward_to_doctors(processed_data)
        if call_type == 'update_eligibility':
            return service_instance.update_eligibility(processed_data)
        return None
    except Exception as exc:
        return [{
            'message': _(failure_message),
            'detail': str(exc)
        }]


def no_auth_validation(failure_message, call_type, service_instance, data):
    try:

        processed_data = {k: v for k, v in data.items() if k not in [
            "client_mutation_id", "client_mutation_label"]}
        if data.get('client_mutation_id') and data.get('client_mutation_id') != '':
            processed_data['json_ext'] = {
                'client_mutation_id': data.get('client_mutation_id')}

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
        service_instance = WorkforceOrganizationEmployeeDesignationServices(
            user)

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
        service_instance = WorkforceOrganizationEmployeeDesignationServices(
            user)

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
        # workforce_employer_id = graphene.UUID()
        workforce_factory_id = graphene.UUID()
        # join_date = graphene.Date()
        # position = graphene.String()
        monthly_earning = graphene.String()
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_employee"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceEmployeeServices(user)

        # workforce_employer_id = data.pop('workforce_employer_id')
        workforce_factory_id = data.pop('workforce_factory_id')
        # join_date = data.pop('join_date')
        # position = data.pop('position')
        monthly_earning = data.pop('monthly_earning')

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission='',
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
                    employee_designation_service = WorkforceEmployeeDesignationServices(
                        user)

                    employee_designation_obj = {
                        # Safely get 'id', default to None if missing
                        "workforce_employee_id": created_obj.get('id', None),
                        # "workforce_company_id": workforce_employer_id,
                        "workforce_factory_id": workforce_factory_id,
                        # "join_date": join_date,
                        "monthly_salary": monthly_earning,  # Safely get 'monthly_earning'
                        # "position": position,  # Safely get 'position'
                    }

                    # Proceed with creating the employee designation
                    d_created_obj = employee_designation_service.create(
                        employee_designation_obj)

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
            required_permission='',
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
            required_permission="",
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
            required_permission=None,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceBankMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateBankMutation"

    class Input(WorkforceBankInputType):
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


class UpdateWorkforceBankMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateBankMutation"

    class Input(WorkforceBankInputType):
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


class CreateWorkforceApplicationMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceApplicationMutation"

    class Input(WorkforceApplicationInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_application"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceApplicationServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission='',
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceApplicationMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceApplicationMutation"

    class Input(WorkforceApplicationInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_application"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceApplicationServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission='',
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceDocumentTypeMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceDocumentTypeMutation"

    class Input(WorkforceDocumentTypeInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_document_type"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceDocumentTypeServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceDocumentTypeMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceDocumentTypeMutation"

    class Input(WorkforceDocumentTypeInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_document_type"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceDocumentTypeServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceDocumentMapMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceDocumentMapMutation"

    class Input(WorkforceDocumentMapInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_document_map"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceDocumentMapServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceDocumentMapMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceDocumentMapMutation"

    class Input(WorkforceDocumentMapInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_document_map"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceDocumentMapServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceUserMutation(mixins.ResolveMixin, JSONWebTokenMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceUserMutation"

    class Arguments:
        name_bn = graphene.String(required=True)
        first_name_en = graphene.String(required=True)
        last_name_en = graphene.String()
        nid = graphene.String(required=True)
        birth_certificate_no = graphene.String()
        phone_number = graphene.String(required=True)
        password = graphene.String(required=True)
        internal_id = graphene.String()
        status = graphene.String()

    internal_id = graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_user"
        service_instance = WorkforceUserServices()

        result = no_auth_validation(
            failure_message=failure_message,
            call_type='create',
            service_instance=service_instance,
            data=data
        )

        if isinstance(result, list):
            raise Exception(result[0]['message'] +
                            ": " + result[0].get('detail', ''))

        return cls(internal_id=result.get('internal_id'))


class UpdateWorkforceUserMutation(mixins.ResolveMixin, JSONWebTokenMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceUserMutation"

    class Arguments:
        name_bn = graphene.String(required=True)
        first_name_en = graphene.String(required=True)
        last_name_en = graphene.String()
        nid = graphene.String(required=True)
        phone_number = graphene.String(required=True)
        password = graphene.String(required=True)
        internal_id = graphene.String()
        status = graphene.String()

    internal_id = graphene.String()

    @classmethod
    def _mutate(cls, root, info, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_user"
        service_instance = WorkforceUserServices()

        result = no_auth_validation(
            failure_message=failure_message,
            call_type='update',
            service_instance=service_instance,
            data=data
        )

        if isinstance(result, list):
            raise Exception(result[0]['message'] +
                            ": " + result[0].get('detail', ''))

        return cls(internal_id=result.get('internal_id'))


class CreateWorkforceOtpMutation(mixins.ResolveMixin, graphene.Mutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceOtpMutation"

    class Arguments:
        name_bn = graphene.String(required=True)
        first_name_en = graphene.String(required=True)
        last_name_en = graphene.String()
        nid = graphene.String()
        birth_certificate_no = graphene.String()
        phone_number = graphene.String(required=True)
        otp = graphene.String()
        creation_date = graphene.String()
        expiry_date = graphene.String()
        attempts = graphene.Int()
        internal_id = graphene.String()
        status = graphene.String()

    internal_id = graphene.String()
    message= graphene.String()
    error= graphene.String()
    code= graphene.String()

    @classmethod
    def mutate(cls, root, info, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_otp"
        service_instance = WorkforceOtpServices()

        result = no_auth_validation(
            failure_message=failure_message,
            call_type='create',
            service_instance=service_instance,
            data=data
        )

        if isinstance(result, list):
            raise Exception(result[0]['message'] +
                            ": " + result[0].get('detail', ''))
            

        return result

class CreateWorkforceApplicationMovementMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceApplicationMovementMutation"

    class Input(WorkforceApplicationMovementInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_application_movement"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceApplicationMovementServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=None,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceApplicationMovementMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceApplicationMovementMutation"

    class Input(WorkforceApplicationMovementInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_application_movement"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceApplicationMovementServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=None,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class WorkforceApplicationBulkUpdateMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "WorkforceApplicationBulkUpdateMutation"

    class Input(OpenIMISMutation.Input):
        applications = graphene.List(WorkforceApplicationBulkUpdateInputType, required=True)

    @classmethod
    def _mutate(cls, user, **data):
        applications_data = data.get("applications", [])
        if not applications_data:
            raise ValidationError("No applications provided for bulk update.")

        bulk_status = applications_data[0].get("status")
        app_ids = [app.get("id") for app in applications_data if app.get("id")]
        results = []

        if bulk_status == "forward_to_doctor":
            try:
                from workforce.services.workforce_application_bulk_movement_services import (
                    WorkforceApplicationBulkMovementServices,
                )
                service_instance = WorkforceApplicationBulkMovementServices(user)
                summary = auth_permission_validation(
                    failure_message="workforce.mutation.failed_to_bulk_forward",
                    required_permission=None,
                    call_type="bulk_forward_to_doctors",
                    service_instance=service_instance,
                    user=user,
                    data={"application_ids": app_ids, "action": bulk_status, "requesting_user": user},
                )
                results.append({"bulk_forward_summary": summary})
            except Exception as e:
                raise ValidationError([f"Bulk forward failed: {e}"])
        else:
            raise ValidationError(f"Unsupported bulk action: {bulk_status}")

        return results


class CreateWorkforceApplicationSummaryMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceApplicationSummaryMutation"

    class Input(WorkforceApplicationSummaryInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_application_summary"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceApplicationSummaryServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceApplicationSummaryMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceApplicationSummaryMutation"

    class Input(WorkforceApplicationSummaryInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_application_summary"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceApplicationSummaryServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceApplicationSummaryMovementMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceApplicationSummaryMovementMutation"

    class Input(WorkforceApplicationSummaryMovementInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_application_summary_movement"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceApplicationSummaryMovementServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceApplicationSummaryMovementMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceApplicationSummaryMovementMutation"

    class Input(WorkforceApplicationSummaryMovementInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_application_summary_movement"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceApplicationSummaryMovementServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceGrantMoneyMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceGrantMoneyMutation"

    class Input(WorkforceGrantMoneyInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_grant_money"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceGrantMoneyServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceGrantMoneyMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceGrantMoneyMutation"

    class Input(WorkforceGrantMoneyInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_grant_money"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceGrantMoneyServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceDiseasesMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceDiseaseMutation"

    class Input(WorkforceDiseasesInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_diseases"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceDiseasesServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceDiseasesMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceDiseasesMutation"

    class Input(WorkforceDiseasesInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_diseases"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceDiseasesServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission=required_permission,
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceEducationMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceEducationMutation"

    class Input(WorkforceEducationInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_education"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceEducationServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission="",
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceEducationMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceEducationMutation"

    class Input(WorkforceEducationInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_education"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceEducationServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission="",
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceEmployeeBankingInfoMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceEmployeeBankingInfoMutation"

    class Input(WorkforceEmployeeBankingInfoInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_employee_banking_info"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceEmployeeBankingInfoServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission="",
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceEmployeeBankingInfoMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceEmployeeBankingInfoMutation"

    class Input(WorkforceEmployeeBankingInfoInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_employee_banking_info"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceEmployeeBankingInfoServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission="",
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceFactoryRegistrationMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceFactoryRegistrationMutation"

    class Input(WorkforceFactoryRegistrationInputType):
        pass

    @classmethod
    def mutate(cls, root, info, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_factory_registration"
        service_instance = WorkforceFactoryRegistrationServices()

        # Unpack ClientIDMutation wrapper
        payload = data.get('input') if 'input' in data else data

        result = no_auth_validation(
            failure_message=failure_message,
            call_type='create',
            service_instance=service_instance,
            data=payload
        )

        return result


class UpdateWorkforceFactoryRegistrationMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceFactoryRegistrationMutation"

    class Input(WorkforceFactoryRegistrationInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        from workforce.models import WorkforceFactoryRegistration
        failure_message = "workforce.mutation.failed_to_update_workforce_factory_registration"
        try:
            if isinstance(user, AnonymousUser) or not user.id:
                raise ValidationError(_("mutation.authentication_required"))
            obj = WorkforceFactoryRegistration.objects.filter(
                id=data.get('id')).first()
            if not obj:
                raise ValidationError(_("Object does not exist"))
            for k, v in data.items():
                if k != 'id' and v is not None:
                    setattr(obj, k, v)
            obj.save(username=user.username)
            return {"success": True, "data": {"id": str(obj.id)}}
        except Exception as exc:
            return [{
                'message': _(failure_message),
                'detail': str(exc)
            }]


class ApprovalWorkforceFactoryRegistrationMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "ApprovalWorkforceFactoryRegistrationMutation"

    class Input(WorkforceFactoryRegistrationApprovalInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_approve_workforce_factory_registration"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceFactoryRegistrationServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission="",
            call_type='approve',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceDependentEligibilityMutation(graphene.Mutation):
    class Arguments:
        workforce_application_id = graphene.String(required=True)

    status = graphene.String()
    data = graphene.Field(lambda: graphene.JSONString)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, workforce_application_id):
        user = info.context.user if hasattr(info.context, 'user') else None
        service_instance = WorkforceEmployeeDependentServices(user)
        update_eligibility = service_instance.update_eligibility(workforce_application_id)
        message= ""
        if update_eligibility["status"]:
            status = "success"
            response_data = {
                "id": str(workforce_application_id),
                "user_id": str(user.id) if user else None
            }
            message = "Update Successfully"
        else:
            status = "error"
            response_data = {
                "id": str(workforce_application_id),
                "user_id": str(user.id) if user else None
            }
            message = update_eligibility["error"]

        return UpdateWorkforceDependentEligibilityMutation(
            status=status,
            data=response_data,
            message=message
        )


class UpdateWorkforceInteractiveUserMutation(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        last_name = graphene.String(required=False)
        other_names = graphene.String(required=False)
        phone = graphene.String(required=False)
        email_id = graphene.String(required=False)

    success = graphene.Boolean()
    user = graphene.Field(WorkforceInteractiveUserGQLType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, **data):
        service_instance = UpdateInteractiveUserServices()
        try:
            updated_user = service_instance.update(data)
            return UpdateWorkforceInteractiveUserMutation(success=True, user=updated_user, errors=[])
        except InteractiveUser.DoesNotExist:
            return UpdateWorkforceInteractiveUserMutation(success=False, user=None, errors=["InteractiveUser not found"])
        except Exception as e:
            return UpdateWorkforceInteractiveUserMutation(success=False, user=None, errors=[str(e)])



class TestWorkforcePaymentMutation(graphene.Mutation):
    class Arguments:
        workforce_application_id = graphene.String(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, **data):
        from workforce.models import WorkforceApplication
        user = info.context.user if hasattr(info.context, 'user') else None
        workforce_application= WorkforceApplication.objects.get(id=data["workforce_application_id"])
        try:
            service_instance = WorkforceEmployeeDependentServices(user)
            service_instance.calculate_eis_amount(data["workforce_application_id"], workforce_application.application_type)
            return TestWorkforcePaymentMutation(success=True, errors=[])
        except InteractiveUser.DoesNotExist:
            return TestWorkforcePaymentMutation(success=False, errors=["Application not found"])
        except Exception as e:
            return TestWorkforcePaymentMutation(success=False, errors=[str(e)])


class CreateWorkforceEisPaymentProcessMutation(graphene.Mutation):
    class Arguments:
        workforce_application_id = graphene.String(required=True)
        month = graphene.String()
        year = graphene.String()

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, **data):
        from workforce.models import WorkforceApplication
        from workforce.models import WorkforceEisPaymentProcess
        from workforce.models import WorkforceEmployeeDependent
        from workforce.services.workforce_employee_dependent_services import WorkforceEmployeeDependentServices
        from workforce.services.workforce_eis_payment_services import WorkforceEisPaymentServices
        try:
            workforce_application_id= data["workforce_application_id"]
            user = info.context.user if hasattr(info.context, 'user') else None
            workforce_application = WorkforceApplication.objects.get(id=data["workforce_application_id"])
            if workforce_application.application_type == "disabilityAssistance":
                if WorkforceEisPaymentProcess.objects.filter(
                        workforce_application_id=data["workforce_application_id"]
                ).exists():
                    return cls(success=False, errors=["Disbursement already exists"])
            if workforce_application.application_type == "financialAssistance":
                if WorkforceEmployeeDependent.objects.filter(
                        workforce_application_id=data["workforce_application_id"], eis_approved_amount__isnull=False
                ).exists():
                    WorkforceEisPaymentServices.create_payment_schedule(user, workforce_application_id)
                else:
                    service = WorkforceEmployeeDependentServices(user)
                    service.calculate_eis_amount(
                        data["workforce_application_id"],
                        workforce_application.application_type
                    )
                    WorkforceEisPaymentServices.create_payment_schedule(user, workforce_application_id)
            WorkforceEisPaymentServices.create_payment_schedule(user, workforce_application_id)
            return cls(success=True, errors=[])
        except Exception as e:
            return cls(success=False, errors=[str(e)])



class CreateWorkforceEisPaymentDisbursementMutation(graphene.Mutation):
    class Arguments:
        workforce_application_id = graphene.String(required=True)
        month = graphene.String(required=False)
        year = graphene.String(required=False)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, **data):
        from workforce.models import WorkforceEisPaymentProcess
        from workforce.models import WorkforceEisPaymentDisbursement
        try:
            user = info.context.user if hasattr(info.context, 'user') else None
            if WorkforceEisPaymentDisbursement.objects.filter(
                    workforce_application_id=data["workforce_application_id"]
            ).exists():
                return cls(success=True, errors=["Disbursement already exists"])
            payment_processes= WorkforceEisPaymentProcess.objects.filter(workforce_application_id=data["workforce_application_id"])
            for process in payment_processes:
                now = datetime.now()
                disburse_obj = WorkforceEisPaymentDisbursement(
                    workforce_application= process.workforce_application,
                    # bank=some_bank_instance,
                    bank_account_no= process.bank_account_no,
                    bank_account_holder_name= process.bank_account_holder_name,
                    eis_payment_type="monthly",
                    eis_calculated_amount= process.eis_calculated_amount,
                    eis_approved_amount= process.eis_approved_amount,
                    eis_monthly_amount=process.eis_monthly_amount,
                    month_index= data["month"] if "month" in data else now.month,  # could be given from frontend, need to make sure
                    year= data["year"] if "year" in data else now.year,  # could be given from frontend, need to make sure
                    disbursement_date= date.today()
                    # disbursed_by=interactive_user,
                )

                disburse_obj.save(username= user.username)
                payment_process = WorkforceEisPaymentProcess.objects.get(id=process.id)
                payment_process.is_disbursed = True
                payment_process.save(username= user.username)
            return cls(success=True, errors=[])
        except Exception as e:
            return cls(success=False, errors=[str(e)])


class CreateWorkforceAllAssociationMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceAllAssociationMutation"

    class Input(WorkforceAllAssociationInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_all_association"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceAllAssociationServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission="",
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceAllAssociationMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceAllAssociationMutation"

    class Input(WorkforceAllAssociationInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_all_association"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceAllAssociationServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission="",
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class CreateWorkforceOtherCompensationInfoMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "CreateWorkforceOtherCompensationInfoMutation"

    class Input(WorkforceOtherCompensationInfoInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_create_workforce_other_compensation_info"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceOtherCompensationInfoServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission="",
            call_type='create',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result


class UpdateWorkforceOtherCompensationInfoMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_module = mutation_module
    _mutation_class = "UpdateWorkforceOtherCompensationInfoMutation"

    class Input(WorkforceOtherCompensationInfoInputType):
        pass

    @classmethod
    def _mutate(cls, user, **data):
        failure_message = "workforce.mutation.failed_to_update_workforce_other_compensation_info"
        required_permission = WorkforceConfig.gql_query_workforces_perms
        service_instance = WorkforceOtherCompensationInfoServices(user)

        result = auth_permission_validation(
            failure_message=failure_message,
            required_permission="",
            call_type='update',
            service_instance=service_instance,
            user=user,
            data=data
        )

        return result



class UpdateWorkforceEisPaymentProcessPaymentTypeMutation(graphene.Mutation):
    class Arguments:
        beneficiary_id = graphene.String(required=True)
        payment_type = graphene.String(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, **data):
        from workforce.models import WorkforceApplication
        from workforce.models import WorkforceEisPaymentProcess
        try:
            user = info.context.user if hasattr(info.context, 'user') else None
            payment_processes = WorkforceEisPaymentProcess.objects.filter(beneficiary_id= data["beneficiary_id"]).update(eis_payment_type=data["payment_type"])
            return cls(success=True, errors=[])
        except Exception as e:
            return cls(success=False, errors=[str(e)])


class UpdateWorkforceEisPaymentProcessApprovalMutation(graphene.Mutation):
    class Arguments:
        beneficiary_id = graphene.String(required=True)
        approved = graphene.String(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, **data):
        from workforce.models import WorkforceEisPaymentProcess
        try:
            user = info.context.user if hasattr(info.context, 'user') else None
            WorkforceEisPaymentProcess.objects.filter(beneficiary_id= data["beneficiary_id"]).update(approved=data["approved"])
            return cls(success=True, errors=[])
        except Exception as e:
            return cls(success=False, errors=[str(e)])


class UpdateWorkforceEisBeneficiaryMutation(graphene.Mutation):
    class Arguments:
        beneficiary_id = graphene.String(required=True)
        increment_amount= graphene.String()
        increment_date= graphene.String()
        decrement_amount= graphene.String()
        decrement_date= graphene.String()
        status= graphene.String()
        beneficiary_status= graphene.String()
        reason = graphene.String()
        remarks = graphene.String()
        remarriage_or_death_date = graphene.String()
        last_live_check_date= graphene.String()
        live_check_remarks = graphene.String()
        other_beneficiary_data= graphene.String()

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, **data):
        from workforce.models import WorkforceEisPaymentProcess
        from workforce.services.workforce_eis_payment_services import WorkforceEisPaymentServices
        try:
            user = info.context.user if hasattr(info.context, 'user') else None
            print(data)
            service= WorkforceEisPaymentServices(user)
            service.update_beneficiary(user, data)
            return cls(success=True, errors=[])
        except Exception as e:
            return cls(success=False, errors=[str(e)])
