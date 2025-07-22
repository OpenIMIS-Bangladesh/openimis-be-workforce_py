import graphene
import os
from django.utils.translation import gettext as _
import graphene_django_optimizer as gql_optimizer
from core.schema import OrderedDjangoFilterConnectionField
from .gql_queries import *
from .gql_mutations import *
from django.db.models import F
from django.utils import timezone
import requests
from graphene.types.generic import GenericScalar


class Query(graphene.ObjectType):
    workforce_representatives = OrderedDjangoFilterConnectionField(
        WorkforceRepresentativeGQLType,
        client_mutation_id=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_organizations = OrderedDjangoFilterConnectionField(
        WorkforceOrganizationGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )

    workforce_organization_units = OrderedDjangoFilterConnectionField(
        WorkforceOrganizationUnitGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_organization_unit_designations = OrderedDjangoFilterConnectionField(
        WorkforceOrganizationUnitDesignationGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_organization_employees = OrderedDjangoFilterConnectionField(
        WorkforceOrganizationEmployeeGQLType,
        username=graphene.String(required=False),
        orderBy=graphene.List(of_type=graphene.String),
    )

    workforce_organization_employee_designations = OrderedDjangoFilterConnectionField(
        WorkforceOrganizationEmployeeDesignationGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )

    workforce_employers = OrderedDjangoFilterConnectionField(
        WorkforceEmployerGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_employer_offices = OrderedDjangoFilterConnectionField(
        WorkforceOfficeGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_employer_factories = OrderedDjangoFilterConnectionField(
        WorkforceFactoryGQLType,
        client_mutation_id=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_employer_employees = OrderedDjangoFilterConnectionField(
        WorkforceEmployeeGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_documents = OrderedDjangoFilterConnectionField(
        WorkforceDocumentGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_banks = OrderedDjangoFilterConnectionField(
        WorkforceBankGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_employee_dependent = OrderedDjangoFilterConnectionField(
        WorkforceEmployeeDependentGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_employee_designation = OrderedDjangoFilterConnectionField(
        WorkforceEmployeeDesignationGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_employee_accident = OrderedDjangoFilterConnectionField(
        WorkforceEmployeeAccidentGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_employee_account_info = OrderedDjangoFilterConnectionField(
        WorkforceEmployeeAccountInfoGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_application = OrderedDjangoFilterConnectionField(
        WorkforceApplicationGQLType,
        client_mutation_id=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
        status_in=graphene.List(graphene.String)
    )
    workforce_document_type = OrderedDjangoFilterConnectionField(
        WorkforceDocumentTypeGQLType,
        client_mutation_id=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_document_map = OrderedDjangoFilterConnectionField(
        WorkforceDocumentMapGQLType,
        client_mutation_id=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_user = OrderedDjangoFilterConnectionField(
        WorkforceUserGQLType,
        client_mutation_id=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_otp = graphene.Field(
        WorkforceOtpGQLType,
        id=graphene.UUID(required=True),
        otp=graphene.String(required=True),
    )
    workforce_application_movement = OrderedDjangoFilterConnectionField(
        WorkforceApplicationMovementGQLType,
        client_mutation_id=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_nid_verification = GenericScalar(
        nid=graphene.NonNull(graphene.String)
    )
    workforce_application_summary = OrderedDjangoFilterConnectionField(
        WorkforceApplicationSummaryGQLType,
        client_mutation_id=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_application_summary_movement = OrderedDjangoFilterConnectionField(
        WorkforceApplicationSummaryMovementGQLType,
        client_mutation_id=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_grant_money = OrderedDjangoFilterConnectionField(
        WorkforceGrantMoneyGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_diseases = OrderedDjangoFilterConnectionField(
        WorkforceDiseasesGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )

    workforce_educations = OrderedDjangoFilterConnectionField(
        WorkforceEducationGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_employee_banking_info = OrderedDjangoFilterConnectionField(
        WorkforceEmployeeBankingInfoGQLType,
        client_mutation_id=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
    )

    def resolve_workforce_representatives(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("unauthorized"))

        service = WorkforceRepresentativeServices(info.context.user)
        query = service.get(**kwargs)
        return gql_optimizer.query(query, info)

    def resolve_workforce_organizations(self, info, **kwargs):
        # if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
        #     raise PermissionDenied(_("unauthorized"))
        pass

    def resolve_workforce_organization_units(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("Unauthorized access"))
        pass

    def resolve_workforce_organization_unit_designations(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("Unauthorized access"))
        pass

    def resolve_workforce_organization_employees(self, info, username=None, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("Unauthorized access"))

        qs = WorkforceOrganizationEmployee.objects.all()

        if username:
            qs = qs.filter(related_user__login_name__iexact=username)

        return qs

    def resolve_workforce_organization_employee_designations(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("Unauthorized access"))
        pass

    def resolve_workforce_employers(self, info, **kwargs):
        # if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
        #     raise PermissionDenied(_("Unauthorized access"))
        pass

    def resolve_workforce_employer_offices(self, info, **kwargs):
        # if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
        #     raise PermissionDenied(_("Unauthorized access"))
        pass

    def resolve_workforce_employer_factories(self, info, **kwargs):
        service = WorkforceFactoryServices(info.context.user)
        query = service.get(**kwargs)
        return gql_optimizer.query(query, info)
    def resolve_workforce_employer_employees(self, info, **kwargs):
        # if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
        #     raise PermissionDenied(_("Unauthorized access"))
        pass
    def resolve_workforce_documents(self, info, **kwargs):
        # if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
        #     raise PermissionDenied(_("Unauthorized access"))
        return WorkforceDocument.objects.filter(is_deleted=False)

    def resolve_workforce_banks(self, info, **kwargs):
        # if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
        #     raise PermissionDenied(_("Unauthorized access"))
        pass
    def resolve_workforce_employee_dependents(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("Unauthorized access"))
        pass
    def resolve_workforce_employee_designations(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("Unauthorized access"))
        pass
    def resolve_workforce_employee_accidents(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("Unauthorized access"))
        pass
    def resolve_workforce_employee_account_infos(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("Unauthorized access"))
        pass
    def resolve_workforce_application(self, info, status_in=None, **kwargs):
        service = WorkforceApplicationServices(info.context.user)
        query = service.get(**kwargs)
        if status_in:
            query = query.filter(status__in=status_in)
        return gql_optimizer.query(query, info)
    def resolve_workforce_document_types(self, info, **kwargs):
        service = WorkforceDocumentTypeServices(info.context.user)
        query = service.get(**kwargs)
        return gql_optimizer.query(query, info)
    def resolve_workforce_user(self, info, **kwargs):
        service = WorkforceUserServices(info.context.user)
        query = service.get(**kwargs)
        return gql_optimizer.query(query, info)
    def resolve_workforce_otp(self, info, id, otp):
        now = timezone.now()
        try:
            otp_obj = WorkforceOtp.objects.only("id", "otp", "status").get(id=id, otp=otp, status="active")

            if otp_obj.expiry_date < now:
                otp_obj.attempts = F('attempts') + 1
                otp_obj.status = 'expired'
                otp_obj.save(update_fields=['status', 'attempts'])

                return WorkforceOtpGQLType(status='expired')

            otp_obj.attempts = F('attempts') + 1
            otp_obj.status = 'used'
            otp_obj.save(update_fields=['status', 'attempts'])

            return WorkforceOtpGQLType(
                status='active',
                name_bn=otp_obj.name_bn,
                first_name_en=otp_obj.first_name_en,
                nid=otp_obj.nid,
                birth_certificate_no=otp_obj.birth_certificate_no,
                phone_number=otp_obj.phone_number
            )

        except WorkforceOtp.DoesNotExist:
            # Wrong OTP or inactive
            try:
                otp_obj = WorkforceOtp.objects.get(id=id)

                otp_obj.attempts = F('attempts') + 1
                otp_obj.save(update_fields=['attempts'])
                otp_obj.refresh_from_db()

                # If too many tries, mark status
                if otp_obj.attempts >= 3 and otp_obj.status == 'active':
                    otp_obj.status = 'too-many-tries'
                    otp_obj.save(update_fields=['status'])

                    return WorkforceOtpGQLType(status='too-many-tries')

                return WorkforceOtpGQLType(status='invalid')

            except WorkforceOtp.DoesNotExist:
                return WorkforceOtpGQLType(status='not-found')

    def resolve_workforce_application_movements(self, info, **kwargs):
        # if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
        #     raise PermissionDenied(_("Unauthorized access"))
        pass

    def resolve_workforce_nid_verification(self, info, nid):
        api_key = os.environ.get('LIMS_API_KEY')
        base_url = os.environ.get('LIMS_API_BASE_URL')
        token_url = f"{base_url}/user/api/v1/users/token"
        token_params = {"apiKey": api_key}

        try:
            token_response = requests.get(token_url, params=token_params, headers={"accept": "application/json"})
            token_response.raise_for_status()
            access_token = token_response.json()["payload"]["access_token"]
        except Exception as e:
            return {"error": f"Token error: {str(e)}"}

        details_url = f"{base_url}/organization/api/v1/workforces/details"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        params = {"nidNumber": nid}

        try:
            details_response = requests.get(details_url, headers=headers, params=params)
            details_response.raise_for_status()
            return details_response.json().get("payload", {})
        except Exception as e:
            return {"error": f"NID fetch error: {str(e)}"}

    def resolve_workforce_application_summary(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("Unauthorized access"))

        service = WorkforceApplicationSummaryServices(info.context.user)
        query = service.get(**kwargs)
        return gql_optimizer.query(query, info)
    def resolve_workforce_application_summary_movement(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("Unauthorized access"))
    def resolve_workforce_grant_money(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("Unauthorized access"))
    def resolve_workforce_diseases(self, info, **kwargs):
        # if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
        #     raise PermissionDenied(_("Unauthorized access"))
        pass

    def resolve_workforce_educations(self, info, **kwargs):
        pass
    def resolve_workforce_employee_banking_info(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("Unauthorized access"))
        pass


class Mutation(graphene.ObjectType):
    create_workforce_representative = CreateWorkforceRepresentativeMutation.Field()
    update_workforce_representative = UpdateWorkforceRepresentativeMutation.Field()

    create_workforce_organization = CreateWorkforceOrganizationMutation.Field()
    update_workforce_organization = UpdateWorkforceOrganizationMutation.Field()

    create_workforce_organization_unit = CreateWorkforceOrganizationUnitMutation.Field()
    update_workforce_organization_unit = UpdateWorkforceOrganizationUnitMutation.Field()

    create_workforce_organization_unit_designation = CreateWorkforceOrganizationUnitDesignationMutation.Field()
    update_workforce_organization_unit_designation = UpdateWorkforceOrganizationUnitDesignationMutation.Field()

    create_workforce_organization_employee = CreateWorkforceOrganizationEmployeeMutation.Field()
    update_workforce_organization_employee = UpdateWorkforceOrganizationEmployeeMutation.Field()

    create_workforce_organization_employee_designation = CreateWorkforceOrganizationEmployeeDesignationMutation.Field()
    update_workforce_organization_employee_designation = UpdateWorkforceOrganizationEmployeeDesignationMutation.Field()

    create_workforce_employer = CreateWorkforceEmployerMutation.Field()
    update_workforce_employer = UpdateWorkforceEmployerMutation.Field()
    update_workforce_employer_status = UpdateWorkforceEmployerStatusMutation.Field()

    create_workforce_employer_office = CreateWorkforceOfficeMutation.Field()
    update_workforce_employer_office = UpdateWorkforceOfficeMutation.Field()

    create_workforce_employer_factory = CreateWorkforceFactoryMutation.Field()
    update_workforce_employer_factory = UpdateWorkforceFactoryMutation.Field()

    create_workforce_employer_employee = CreateWorkforceEmployeeMutation.Field()
    update_workforce_employer_employee = UpdateWorkforceEmployeeMutation.Field()

    create_workforce_document = CreateWorkforceDocumentMutation.Field()
    update_workforce_document = UpdateWorkforceDocumentMutation.Field()

    create_workforce_bank = CreateWorkforceBankMutation.Field()
    update_workforce_bank = UpdateWorkforceBankMutation.Field()

    create_workforce_employee_dependent = CreateWorkforceEmployeeDependentMutation.Field()
    update_workforce_employee_dependent = UpdateWorkforceEmployeeDependentMutation.Field()

    create_workforce_employee_designation = CreateWorkforceEmployeeDesignationMutation.Field()
    update_workforce_employee_designation = UpdateWorkforceEmployeeDesignationMutation.Field()

    create_workforce_employee_accident = CreateWorkforceEmployeeAccidentMutation.Field()
    update_workforce_employee_accident = UpdateWorkforceEmployeeAccidentMutation.Field()

    create_workforce_employee_account_info = CreateWorkforceEmployeeAccountInfoMutation.Field()
    update_workforce_employee_account_info = UpdateWorkforceEmployeeAccountInfoMutation.Field()

    create_workforce_application = CreateWorkforceApplicationMutation.Field()
    update_workforce_application = UpdateWorkforceApplicationMutation.Field()

    create_workforce_document_type = CreateWorkforceDocumentTypeMutation.Field()
    update_workforce_document_type = UpdateWorkforceDocumentTypeMutation.Field()

    create_workforce_document_map = CreateWorkforceDocumentMapMutation.Field()
    update_workforce_document_map = UpdateWorkforceDocumentMapMutation.Field()

    create_workforce_user = CreateWorkforceUserMutation.Field()
    update_workforce_user = UpdateWorkforceUserMutation.Field()

    create_workforce_otp = CreateWorkforceOtpMutation.Field()

    create_workforce_application_movement = CreateWorkforceApplicationMovementMutation.Field()
    update_workforce_application_movement = UpdateWorkforceApplicationMovementMutation.Field()

    create_workforce_application_summary = CreateWorkforceApplicationSummaryMutation.Field()
    update_workforce_application_summary = UpdateWorkforceApplicationSummaryMutation.Field()

    create_workforce_application_summary_movement = CreateWorkforceApplicationSummaryMovementMutation.Field()
    update_workforce_application_summary_movement = UpdateWorkforceApplicationSummaryMovementMutation.Field()

    create_workforce_grant_money = CreateWorkforceGrantMoneyMutation.Field()
    update_workforce_grant_money = UpdateWorkforceGrantMoneyMutation.Field()

    create_workforce_diseases = CreateWorkforceDiseasesMutation.Field()
    update_workforce_diseases = UpdateWorkforceDiseasesMutation.Field()

    create_workforce_education = CreateWorkforceEducationMutation.Field()
    update_workforce_education = UpdateWorkforceEducationMutation.Field()

    create_workforce_employee_banking_info = CreateWorkforceEmployeeBankingInfoMutation.Field()
    update_workforce_employee_banking_info = UpdateWorkforceEmployeeBankingInfoMutation.Field()
