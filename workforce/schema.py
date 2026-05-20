import os
from collections import defaultdict

import graphene
import graphene_django_optimizer as gql_optimizer
import requests
from django.db.models import Count
from django.db.models import F
from django.db.models import OuterRef, Subquery
from django.db.models import Q
from django.utils.timezone import now
from django.utils.translation import gettext as _
from graphene.types.generic import GenericScalar
from graphql import GraphQLError

from core.models.user import InteractiveUser
from core.models.user import UserRole
from core.schema import OrderedDjangoFilterConnectionField
from .gql_mutations import *
from .gql_queries import *
from .models import *
from .services.workforce_committee_user_services import WorkforceCommitteeUserServices
from django.db.models.expressions import RawSQL


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
        search_name=graphene.String(required=False),
        all_association_id_in= graphene.List(graphene.String),
        client_mutation_id=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_employer_employees = OrderedDjangoFilterConnectionField(
        WorkforceEmployeeGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_documents = OrderedDjangoFilterConnectionField(
        WorkforceDocumentGQLType,
        workforce_factory_id= graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_banks = OrderedDjangoFilterConnectionField(
        WorkforceBankGQLType,
        orderBy=graphene.List(of_type=graphene.String),
        get_unique=graphene.String(required=False, description="Get unique bank names only")
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
        status_in=graphene.List(graphene.String),
        association_type_in=graphene.List(graphene.String),
        application_type_in=graphene.List(graphene.String),
        submitted_by_in=graphene.List(graphene.String),
        application_to=graphene.String(),
        application_from=graphene.String(),
        organization_type_in=graphene.List(graphene.String),
        is_reverted=graphene.Boolean(),
        date_created_from= graphene.String(),
        date_created_to= graphene.String(),
        all_association_id_in= graphene.List(graphene.String),
        eis_application_summary_id= graphene.String()
    )

    workforce_document_types = OrderedDjangoFilterConnectionField(
        WorkforceDocumentTypeGQLType,
        client_mutation_id=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
        application_for_in=graphene.List(graphene.String),
        document_type_in=graphene.List(graphene.String)
    )
    workforce_document_map = graphene.List(
        WorkforceDocumentMapGQLType,
        workforce_application_id=graphene.String(),
        workforce_document_id=graphene.String(),
        verified_by_id=graphene.String(),
        verified_by_role_id=graphene.String(),
        status=graphene.String(),
        verification_date=graphene.String(),
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
        status_in=graphene.List(graphene.String),
        section_type_in=graphene.List(graphene.String),
        organization_type_in=graphene.List(graphene.String),
        user_id= graphene.String()
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
    workforce_missing_documents = GenericScalar(
        application_id=graphene.String(),
    )
    workforce_factory_registrations = OrderedDjangoFilterConnectionField(
        WorkforceFactoryRegistrationGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_postoffice = graphene.List(
        WorkforcePostofficeGQLType,
        orderBy=graphene.List(of_type=graphene.String),
        w_code_id=graphene.String(required=False),
    )
    workforce_user_role = graphene.List(
        WorkforceUserRoleGQLType,
        role_id_in=graphene.List(graphene.String, required=False),
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_application_matrix = graphene.List(
        WorkforceApplicationMatrixGQLType,
        organization_type=graphene.String(required=False),
        last_months=graphene.String(required=False),
        date_between=graphene.List(of_type=graphene.String, required=False)
    )
    workforce_genderwise_matrix = graphene.List(
        WorkforceGenderwiseMatrixGQLType,
        organization_type=graphene.String(required=False),
        last_months=graphene.String(required=False),
        date_between=graphene.List(of_type=graphene.String, required=False)
    )
    workforce_monthwise_applications = graphene.List(
        WorkforceMonthwiseApplicationsGQLType,
        organization_type=graphene.String(required=False),
        months_between=graphene.String(required=False),
        date_between=graphene.List(of_type=graphene.String, required=False),
    )
    workforce_eis_calculation = graphene.Field(
        WorkforceEISCalculationGQLType,
        parameters=graphene.JSONString(required=False),
        worker=graphene.JSONString(required=False),
        dependents=graphene.JSONString(required=False),
        number_of_dependents=graphene.String(required=False),
    )
    workforce_application_timewise_matrix = graphene.Field(
        WorkforceApplicationTimewiseMatrixGQLType,
        application_type_in=graphene.List(graphene.String, required=False),
        organization_type=graphene.String(required=False),
        day_count=graphene.String(required=False),
    )

    workforce_employer_factories_public = graphene.Field(
        WorkforceFactoryGQLType,
        client_mutation_id=graphene.String(required=False),
    )

    workforce_interactive_user = graphene.Field(
        WorkforceInteractiveUserGQLType,
        id=graphene.String(required=True),
        last_name=graphene.String(required=False),
        other_names=graphene.String(required=False),
        phone=graphene.String(required=False),
        email_id=graphene.String(required=False)
    )

    workforce_interactive_users = graphene.List(
        WorkforceInteractiveUserGQLType,
        id=graphene.String(required=False),
        login_name=graphene.String(required=False),
    )

    workforce_eis_payment_process = graphene.List(
        WorkforceEisPaymentProcessGQLType,
        workforce_application_id=graphene.String(),
        beneficiary_id= graphene.String(),
        workforce_application_tracking_number = graphene.String(),
        workforce_factory_id=graphene.String(),
        all_association_id= graphene.String(),
        workforce_application_id_in=graphene.List(of_type=graphene.String),
        month=graphene.String(),
        year=graphene.String(),
        status= graphene.String(),
        beneficiary_status=graphene.String(),
        approved= graphene.String(),
        approval_date_from= graphene.String(),
        approval_date_to= graphene.String(),
        accident_date_from= graphene.String(),
        accident_date_to= graphene.String(),
        not_in_stage= graphene.String()
    )


    workforce_eis_payment_disbursement_stage = graphene.List(
        WorkforceEisPaymentDisbursementStageGQLType,
        month=graphene.String(),
        year=graphene.String(),
        workforce_factory_id= graphene.String(),
        all_association_id= graphene.String(),
        is_disbursed= graphene.String(),
        not_in_disburse= graphene.String(),
        workforce_eis_bank_advice_id= graphene.String()
    )


    workforce_eis_payment_disbursement = graphene.List(
        WorkforceEisPaymentDisbursementGQLType,
        workforce_application_id=graphene.String(),
        workforce_application_id_in=graphene.List(of_type=graphene.String),
        month=graphene.String(),
        year=graphene.String(),
    )

    workforce_all_association = OrderedDjangoFilterConnectionField(
        WorkforceAllAssociationGQLType,
        id_in= graphene.List(of_type=graphene.String),
        client_mutation_id=graphene.String(required=False),
    )

    workforce_other_compensation_info = OrderedDjangoFilterConnectionField(
        WorkforceOtherCompensationInfoGQLType,
        client_mutation_id=graphene.String(required=False),
        workforce_application_id=graphene.String(required=False)
    )

    workforce_signatures = graphene.Field(
        graphene.List(GenericScalar),
        related_users=graphene.NonNull(
            graphene.List(graphene.NonNull(graphene.String))
        ),
    )

    workforce_association_user_map = OrderedDjangoFilterConnectionField(
        WorkforceAssociationUserMapGQLType,
        client_mutation_id=graphene.String(required=False),
        all_association_id= graphene.String(),
        all_association_id_in= graphene.List(graphene.String),
        user_id= graphene.Int()
    )

    workforce_eis_bank_advice = graphene.List(
        WorkforceEisBankAdviceGQLType,
        advice_date=graphene.String(),
        is_confirmed=graphene.Boolean(),
        month=graphene.String(),
        year=graphene.String(),
    )

    workforce_committees = graphene.List(
        WorkforceCommitteeGQLType,
        organization_type=graphene.String(),
        approval_type=graphene.String(),
        client_mutation_id=graphene.String(required=False),
        orderBy=graphene.List(of_type=graphene.String),
    )

    workforce_committee_association_maps = graphene.List(
        WorkforceCommitteeAssociationMapGQLType,
        client_mutation_id=graphene.String(required=False),
        orderBy=graphene.List(of_type=graphene.String),
    )

    workforce_committee_users = graphene.List(
        WorkforceCommitteeUserGQLType,
        client_mutation_id=graphene.String(required=False),
        orderBy=graphene.List(of_type=graphene.String),
    )

    workforce_committee_user_maps = graphene.List(
        WorkforceCommitteeUserMapGQLType,
        committee_id= graphene.String(),
        user_id_in= graphene.List(of_type=graphene.String),
        client_mutation_id=graphene.String(required=False),
        orderBy=graphene.List(of_type=graphene.String),
    )

    workforce_committee_bank_advice_maps = OrderedDjangoFilterConnectionField(
        WorkforceCommitteeBankAdviceMapGQLType,
        committee_id=graphene.String(),
        client_mutation_id=graphene.String(required=False),
        orderBy=graphene.List(of_type=graphene.String),
    )


    workforce_notifications = OrderedDjangoFilterConnectionField(
        WorkforceNotificationGQLType,
        logged_in_user_id=graphene.String(required=True),
        orderBy=graphene.List(of_type=graphene.String),
    )

    fetch_user_role_by_user_id = graphene.List(
        WorkforceUserRoleGQLType,
        user_id= graphene.String(required=True),
    )


    fetch_noa_signature_by_approvers = graphene.Field(
        WorkforceDocumentGQLType,
        user_id_in= graphene.List(of_type=graphene.String),
    )

    fetch_workforce_noa_signer_user_by_approvers = graphene.Field(
        WorkforceCommitteeUserMapGQLType,
        user_id_in= graphene.List(of_type=graphene.String),
    )

    website_legal_guidelines = graphene.Field(
        WebsiteLegalGuidelineGQLType,
        id= graphene.String,
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

    def resolve_workforce_employer_factories(self, info,search_name=None, all_association_id_in=None, **kwargs):
        service = WorkforceFactoryServices(info.context.user)
        query = service.get(**kwargs)
        if search_name:
            query = query.filter(
                Q(name_en__icontains=search_name) |
                Q(name_bn__icontains=search_name)
            )

        if all_association_id_in:
            query= query.filter(all_association_id__in= all_association_id_in)
        return gql_optimizer.query(query, info)

    def resolve_workforce_employer_factories_public(self, info, **kwargs):
        model = WorkforceFactory
        filters = Q(is_deleted=False)

        client_mutation_id = kwargs.get("client_mutation_id")
        if client_mutation_id:
            filters &= Q(json_ext__contains={"client_mutation_id": client_mutation_id})

        instance = model.objects.filter(filters).first()
        return instance

    def resolve_workforce_employer_employees(self, info, **kwargs):
        # if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
        #     raise PermissionDenied(_("Unauthorized access"))
        pass
    def resolve_workforce_documents(self, info, workforce_factory_id=None, **kwargs):
        # if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
        #     raise PermissionDenied(_("Unauthorized access"))
        # return WorkforceDocument.objects.filter(is_deleted=False)
        service = WorkforceDocumentServices(info.context.user)
        query = service.get(**kwargs)
        if workforce_factory_id:
            query= query.filter(factory_id=workforce_factory_id)
        return gql_optimizer.query(query, info)

    def resolve_workforce_banks(self, info, get_unique=None, **kwargs):
        query = Bank.objects.filter(is_deleted=False)

        for key, value in kwargs.items():
            if hasattr(Bank, key) and value is not None:
                query = query.filter(**{key: value})

        # Apply unique filtering if requested
        if get_unique == "true" or get_unique == "True":
            query = query.distinct('district_name_en', 'district_name_bn')

        return gql_optimizer.query(query, info)
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

    def resolve_workforce_application(
            self,
            info,
            status_in=None,
            association_type_in=None,
            application_type_in=None,
            submitted_by_in=None,
            application_to=None,
            application_from=None,
            organization_type_in=None,
            is_reverted=None,
            date_created_from= None,
            date_created_to= None,
            eis_verified = None,
            all_association_id_in= None,
            eis_application_summary_id = None,
            **kwargs
    ):
        service = WorkforceApplicationServices(info.context.user)
        query = service.get(**kwargs)

        if status_in:
            query = query.filter(status__in=status_in)
        if association_type_in:
            query = query.filter(association_type__in=association_type_in)
        if application_type_in:
            query = query.filter(application_type__in=application_type_in)
        if submitted_by_in:
            query = query.filter(submitted_by__in=submitted_by_in)
        if organization_type_in:
            query = query.filter(organization_type__in=organization_type_in)

        if application_to:
            application_to_id = application_to
            query = query.filter(application__application_to_id=application_to_id).distinct()

        if application_from:
            application_from_id = application_from
            query = query.filter(application__application_from_id=application_from_id).distinct()

        if is_reverted:
            query = query.filter(application__is_reverted=is_reverted).distinct()

        if application_to:
            try:
                app_to_id = int(application_to)
            except ValueError:
                app_to_id = None

            if app_to_id:
                latest_receive_subquery = WorkforceApplicationMovement.objects.filter(
                    application_id=OuterRef("pk"),
                    application_to_id=app_to_id,
                ).distinct().order_by("-date_created").values("date_created")[:1]

                query = query.annotate(applicationReceiveDate=Subquery(latest_receive_subquery))

        if application_from:
            try:
                app_from_id = int(application_from)
            except ValueError:
                app_from_id = None

            if app_from_id:
                latest_forward_subquery = WorkforceApplicationMovement.objects.filter(
                    application_id=OuterRef("pk"),
                    application_from_id=app_from_id,
                ).distinct().order_by("-date_created").values("date_created")[:1]

                query = query.annotate(applicationForwardDate=Subquery(latest_forward_subquery))

        #new added for searching by raduan
        if date_created_from:
            query = query.filter(date_created__gte=date_created_from)
        if date_created_to:
            query = query.filter(date_created__lte=date_created_to)

        if eis_verified:
            query = query.filter(eis_verified=eis_verified)

        if all_association_id_in:
            query = query.filter(employee_factory__all_association_id__in= all_association_id_in)

        if eis_application_summary_id:
            query = query.filter(eis_application_summary_id=eis_application_summary_id)


        latest_movement_subquery = WorkforceApplicationMovement.objects.filter(
            application_id=OuterRef("pk")
        ).distinct().order_by("-date_created").values("date_created")[:1]

        query = query.annotate(lastMovementDate=Subquery(latest_movement_subquery))

        return gql_optimizer.query(query, info)

    def resolve_workforce_document_types(self, info, application_for_in=None, document_type_in=None, **kwargs):
        service = WorkforceDocumentTypeServices(info.context.user)
        query = service.get(**kwargs)
        query = query.filter(is_deleted=False)

        if application_for_in:
            query = query.filter(application_for__in=application_for_in)
        if document_type_in:
            query = query.filter(document_type__in=document_type_in)
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

    def resolve_workforce_application_summary(self, info, status_in=None, section_type_in=None, organization_type_in=None, user_id=None, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("Unauthorized access"))

        service = WorkforceApplicationSummaryServices(info.context.user)
        query = service.get(**kwargs)
        if status_in:
            query = query.filter(status__in=status_in)
        if section_type_in:
            query = query.filter(section_type__in=section_type_in)
        if organization_type_in:
            query = query.filter(organization_type__in=organization_type_in)


        #check if there is any application in the summary. Experimental block by Tahir
        # recent_threshold = timezone.now() - timedelta(seconds=30)
        valid_summary_ids = []
        client_mutation_id = kwargs.get("client_mutation_id", None)
        for summary in query:
            applications = WorkforceApplication.objects.filter(
                Q(blwf_application_summary_id=summary.id) |
                Q(cf_application_summary_id=summary.id) |
                Q(eis_application_summary_id=summary.id)
            )

            if applications.exists() or (client_mutation_id is not None and client_mutation_id!=""):
                # or summary.date_created >= recent_threshold:
                valid_summary_ids.append(summary.id)
        query = query.filter(id__in=valid_summary_ids)

        if user_id:
            matched_ids = []

            for data in query:
                try:
                    user_ids = json.loads(data.user_ids or "[]")
                except json.JSONDecodeError:
                    user_ids = []

                if user_id in user_ids:
                    matched_ids.append(data.id)

            query = query.filter(id__in=matched_ids)
        #block end. You can remove this block if necessary.

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

    def resolve_workforce_postoffice(self, info, orderBy=None, w_code_id=None, **kwargs):
        qs = WorkforcePostoffice.objects.all()

        if w_code_id:
            qs = qs.filter(w_code_id=w_code_id)
        if orderBy:
            qs = qs.order_by(*orderBy)

        objs = qs.values("id", "w_code", "post_code", "post_office", "name_en", "name_bn", "status")

        return [
            {
                "id": str(obj["id"]) if obj.get("id") is not None else None,
                "w_code": obj.get("w_code"),
                "post_code": obj.get("post_code"),
                "post_office": obj.get("post_office"),
                "name_en": obj.get("name_en"),
                "name_bn": obj.get("name_bn"),
                "status": obj.get("status"),
            }
            for obj in objs
        ]

    def resolve_workforce_user_role(self, info, role_id_in=None, orderBy=None, **kwargs):
        qs = UserRole.objects.filter(validity_to__isnull=True)
        if role_id_in:
            qs = qs.filter(role_id__in=role_id_in)
        if orderBy:
            qs = qs.order_by(*orderBy)

        rows = list(qs.values("id", "role_id", "user_id"))
        user_ids = [r["user_id"] for r in rows]

        iu_qs = InteractiveUser.objects.filter(id__in=user_ids).values("id", "last_name", "other_names")
        iu_by_id = {u["id"]: u for u in iu_qs}

        return [
            WorkforceUserRoleGQLType(
                id=r["id"],
                role_id=r["role_id"],
                user_id=r["user_id"],
                last_name=iu_by_id.get(r["user_id"], {}).get("last_name"),
                other_names=iu_by_id.get(r["user_id"], {}).get("other_names"),
            )
            for r in rows
        ]

    def resolve_workforce_application_matrix(self, info, organization_type=None, date_between=None, last_months=None, **kwargs):
        category_map = {
            "medical": {
                "cf": ["medicalAssistance"],
                "blwf": ["medicalDonation"],
            },
            "educational": {
                "cf": ["scholarship"],
                "blwf": ["educationGrant"],
            },
            "death": {
                "cf": ["financialAssistance"],
                "eis": ["financialAssistance"],
                "blwf": ["deadlyGrant"],
            },
            "maternityGrant": {
                "cf": ["maternityGrant"],
                "blwf": ["maternityGrant"],
            },
            "disabilityAssistance": {
                "cf": ["disabilityAssistance"],
                "eis": ["disabilityAssistance"],
                "blwf": [],
            },
        }

        qs = WorkforceApplication.objects.all()

        if organization_type:
            qs = qs.filter(organization_type=organization_type)

        # Prevent using both filters at the same time
        if last_months and date_between:
            raise GraphQLError("You can only filter by either 'lastMonths' or 'dateBetween', not both.")

        # Filter by last N months
        if last_months:
            now = timezone.now()
            start_date = now - timedelta(days=30 * int(last_months))
            qs = qs.filter(date_created__gte=start_date)

        # Filter between specific dates
        if date_between and len(date_between) == 2:
            try:
                start_date = datetime.fromisoformat(date_between[0])
                end_date = datetime.fromisoformat(date_between[1])
            except ValueError:
                raise GraphQLError(
                    "Invalid date format in 'date_between'. Use ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS")
            qs = qs.filter(date_created__range=(start_date, end_date))

        # Reverse map for category lookup
        reverse_map = {}
        for category, org_map in category_map.items():
            for org_type, app_types in org_map.items():
                for app_type in app_types:
                    reverse_map[(org_type, app_type)] = category

        category_counts = {
            category: {"application_count": 0, "approved_count": 0, "rejected_count": 0}
            for category in category_map.keys()
        }

        # Summation across all categories
        # total_counts = {"application_count": 0, "approved_count": 0, "rejected_count": 0}

        for app in qs.values("organization_type", "application_type", "status"):
            category = reverse_map.get((app["organization_type"], app["application_type"]))
            if not category:
                continue

            category_counts[category]["application_count"] += 1
            # total_counts["application_count"] += 1

            if app["status"] in ("approved_by_dg", "approved_by_director"):
                category_counts[category]["approved_count"] += 1
                # total_counts["approved_count"] += 1

            elif app["status"] in ("rejected", "revert"):
                category_counts[category]["rejected_count"] += 1
                # total_counts["rejected_count"] += 1

        result = []
        for category, counts in category_counts.items():
            result.append(
                WorkforceApplicationMatrixGQLType(
                    application_type=category,
                    application_count=str(counts["application_count"]),
                    approved_count=str(counts["approved_count"]),
                    rejected_count=str(counts["rejected_count"]),
                )
            )

        return result

    def resolve_workforce_genderwise_matrix(self, info, organization_type=None, date_between=None, last_months=None, **kwargs):
        qs = WorkforceApplication.objects.all()

        if organization_type:
            qs = qs.filter(organization_type=organization_type)
        else:
            qs = qs.exclude(organization_type="eis")
        if last_months and date_between:
            raise GraphQLError("You can only filter by either 'lastMonths' or 'dateBetween', not both.")

        if last_months:
            now = timezone.now()
            start_date = now - timedelta(days=30 * int(last_months))
            qs = qs.filter(date_created__gte=start_date)

        if date_between and len(date_between) == 2:
            try:
                start_date = datetime.fromisoformat(date_between[0])
                end_date = datetime.fromisoformat(date_between[1])
            except ValueError:
                raise GraphQLError(
                    "Invalid date format in 'date_between'. Use ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS")
            qs = qs.filter(date_created__range=(start_date, end_date))

        employee_ids = list(qs.values_list("workforce_employee_id", flat=True).distinct())
        employee_ids = [eid for eid in employee_ids if eid is not None]
        total_applicant_count = len(employee_ids)

        applicant_gender_qs = (
            WorkforceEmployee.objects
            .filter(id__in=employee_ids)
            .values("gender")
            .annotate(cnt=Count("id"))
        )

        male_applicant = 0
        female_applicant = 0
        for row in applicant_gender_qs:
            cnt = row["cnt"]
            gender_val = (row["gender"] or "").strip().lower()
            if gender_val.startswith("m"):
                male_applicant += cnt
            elif gender_val.startswith("f"):
                female_applicant += cnt

        app_ids = list(qs.values_list("id", flat=True).distinct())
        dependent_gender_qs = (
            WorkforceEmployeeDependent.objects
            .filter(workforce_application_id__in=app_ids)
            .values("gender")
            .annotate(cnt=Count("id"))
        )

        male_dependent = 0
        female_dependent = 0
        total_dependent_count = 0
        for row in dependent_gender_qs:
            cnt = row["cnt"]
            total_dependent_count += cnt
            gender_val = (row["gender"] or "").strip().lower()
            if gender_val.startswith("m"):
                male_dependent += cnt
            elif gender_val.startswith("f"):
                female_dependent += cnt

        # Total benefit amount (grant_money)
        amounts = qs.values_list("grant_amount", flat=True)
        total_grant_money = sum(float(a) for a in amounts if a not in [None, ""])

        return [
            WorkforceGenderwiseMatrixGQLType(
                total_applicant=str(total_applicant_count),
                total_dependent=str(total_dependent_count),
                male_applicant=str(male_applicant),
                female_applicant=str(female_applicant),
                male_dependent=str(male_dependent),
                female_dependent=str(female_dependent),
                total_benefit_amount=str(total_grant_money),
            )
        ]

    def resolve_workforce_monthwise_applications(
            self, info, organization_type=None, months_between=None, date_between=None, **kwargs
    ):
        category_map = {
            "medical": {
                "cf": ["medicalAssistance"],
                "blwf": ["medicalDonation"],
            },
            "educational": {
                "cf": ["scholarship"],
                "blwf": ["educationGrant"],
            },
            "death": {
                "cf": ["financialAssistance"],
                "eis" : ["financialAssistance"],
                "blwf": ["deadlyGrant"],
            },
            "maternityGrant": {
                "cf": ["maternityGrant"],
                "blwf": ["maternityGrant"],
            },
            "disabilityAssistance": {
                "cf": ["disabilityAssistance"],
                "eis": ["disabilityAssistance"],
                "blwf": [],
            },
        }

        # reverse map for lookup
        reverse_map = {}
        for category, org_map in category_map.items():
            for org_type, app_types in org_map.items():
                for app_type in app_types:
                    reverse_map[(org_type, app_type)] = category

        qs = WorkforceApplication.objects.all()

        if organization_type:
            qs = qs.filter(organization_type=organization_type)

        # ensure exactly one filter
        if (months_between and date_between) or (not months_between and not date_between):
            raise GraphQLError("Provide either 'months_between' or 'date_between', not both or none.")

        months_list = []
        if months_between:
            try:
                months_between = int(months_between)
            except ValueError:
                raise GraphQLError("'months_between' must be an integer string")

            now = timezone.now()
            # generate last N months (including current)
            for i in range(months_between):
                month_date = (now.replace(day=1) - timedelta(days=30 * i))
                months_list.append(month_date.month)
            months_list = sorted(set(months_list))

            start_date = (now.replace(day=1) - timedelta(days=30 * (months_between - 1))).replace(day=1)
            qs = qs.filter(date_created__gte=start_date)

        if date_between and len(date_between) == 2:
            try:
                start_date = datetime.fromisoformat(date_between[0])
                end_date = datetime.fromisoformat(date_between[1])
            except ValueError:
                raise GraphQLError(
                    "Invalid date format in 'date_between'. Use ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS"
                )
            qs = qs.filter(date_created__range=(start_date, end_date))

            # build months list from range
            months_list = sorted(set(
                (start_date + timedelta(days=i)).month
                for i in range((end_date - start_date).days + 1)
            ))

        # annotate by month
        apps = qs.values("organization_type", "application_type", "date_created__month")

        # group counts
        monthly_data = defaultdict(lambda: {cat: 0 for cat in category_map.keys()})
        for app in apps:
            month_num = app["date_created__month"]
            category = reverse_map.get((app["organization_type"], app["application_type"]))
            if not category:
                continue
            monthly_data[month_num][category] += 1

        result = []
        for month_num in months_list:
            data = monthly_data[month_num]
            result.append(
                WorkforceMonthwiseApplicationsGQLType(
                    month=str(month_num),
                    medical=str(data["medical"]),
                    educational=str(data["educational"]),
                    death=str(data["death"]),
                    maternityGrant=str(data["maternityGrant"]),
                    disabilityAssistance=str(data["disabilityAssistance"]),
                )
            )

        return result

    def resolve_workforce_eis_calculation(self, info, parameters=None, worker=None, dependents=None,
                                          number_of_dependents=None):
        try:
            payload = {
                "parameters": parameters,
                "Worker": worker,
                "Number of dependents": str(number_of_dependents),
                "Dependents": dependents,
            }

            response = requests.post(os.environ.get("CALCULATION_API_URL"), json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()

            key_map = {
                "PV factor": "pv_factor",
                "PV Total pension": "pv_total_pension",
                "PV Top-Up pension": "pv_topup_pension",
                "Initial replacement rate": "initial_replacement_rate",
                "Total initial monthly pension": "total_initial_monthly_pension",
                "Top-up monthly pension": "topup_monthly_pension",
            }

            def map_keys(obj):
                if isinstance(obj, dict):
                    new_obj = {}
                    for k, v in obj.items():
                        new_key = key_map.get(k, k)
                        if isinstance(v, (dict, list)):
                            new_obj[new_key] = map_keys(v)
                        elif v is None:
                            new_obj[new_key] = "null"
                        else:
                            new_obj[new_key] = str(v)
                    return new_obj
                elif isinstance(obj, list):
                    return [map_keys(i) for i in obj]
                else:
                    return str(obj)

            result = map_keys(result)
            return result

        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "filename": None,
                "data": {"results": [], "total": {}},
                "error": str(e),
            }

    def resolve_workforce_application_timewise_matrix(self, info, application_type_in=None, organization_type=None,
                                                      day_count=None, **kwargs):
        qs = WorkforceApplication.objects.exclude(
            status__in=[
                "approved_by_dg",
                "approved_by_director",
                "draft",
                "revert",
                "reject",
            ]
        )

        if organization_type:
            qs = qs.filter(organization_type=organization_type)

        if application_type_in:
            qs = qs.filter(application_type__in=application_type_in)

        latest_movement = WorkforceApplicationMovement.objects.filter(
            application_id=OuterRef("id")
        ).order_by("-date_created")

        qs = qs.annotate(
            last_date_created=Subquery(latest_movement.values("date_created")[:1]),
            last_application_to_id=Subquery(latest_movement.values("application_to_id")[:1]),
        )

        if day_count:
            now_time = now()

            ranges = {
                "1": (0, 1),
                "3": (1, 3),
                "7": (3, 7),
                "10": (7, 10),
                "15": (10, 15),
                "15+": (15, None),
            }

            lower, upper = ranges.get(day_count, (None, None))

            if lower is not None:
                lower_time = now_time - timedelta(days=upper) if upper else None
                upper_time = now_time - timedelta(days=lower)

                if upper and lower_time:
                    qs = qs.filter(last_date_created__lte=upper_time, last_date_created__gt=lower_time)
                elif lower is not None and upper is None:
                    qs = qs.filter(last_date_created__lte=now_time - timedelta(days=15))
                else:
                    qs = qs.filter(last_date_created__gte=now_time - timedelta(days=1))

        day_wise_count = {"1": 0, "3": 0, "7": 0, "10": 0, "15": 0, "more_than_15": 0}
        now_time = now()

        for app in qs:
            if not app.last_date_created:
                continue

            diff = (now_time - app.last_date_created).days

            if diff < 1:
                day_wise_count["1"] += 1
            elif diff < 3:
                day_wise_count["3"] += 1
            elif diff < 7:
                day_wise_count["7"] += 1
            elif diff < 10:
                day_wise_count["10"] += 1
            elif diff < 15:
                day_wise_count["15"] += 1
            else:
                day_wise_count["more_than_15"] += 1

        user_ids = [app.last_application_to_id for app in qs if app.last_application_to_id]
        role_wise_data = []

        if user_ids:
            user_app_map = {}
            for app in qs:
                if app.last_application_to_id:
                    user_app_map.setdefault(app.last_application_to_id, []).append(app.id)

            users = InteractiveUser.objects.filter(id__in=user_app_map.keys()).prefetch_related("user_roles__role")

            for user in users:
                apps_for_user = user_app_map.get(user.id, [])
                if not apps_for_user:
                    continue

                roles = user.user_roles.all()
                role_names = list({r.role.name for r in roles}) if roles else ["No Role"]

                role_wise_data.append({
                    "id": user.id,
                    "last_name": user.last_name,
                    "other_names": user.other_names,
                    "role_names": role_names,
                    "application_count": len(apps_for_user),
                })

        return WorkforceApplicationTimewiseMatrixGQLType(
            total_application_count=qs.count(),
            day_wise_count=DayWiseCountGQLType(
                day1=day_wise_count["1"],
                day3=day_wise_count["3"],
                day7=day_wise_count["7"],
                day10=day_wise_count["10"],
                day15=day_wise_count["15"],
                moreThan15=day_wise_count["more_than_15"],
            ),
            role_wise_count=[
                RoleWiseCountGQLType(
                    roleName=", ".join(item["role_names"]),
                    userId=item["id"],
                    lastName=item["last_name"],
                    otherNames=item["other_names"],
                    applicationCount=item["application_count"],
                )
                for item in role_wise_data
            ],
        )

    def resolve_workforce_interactive_user(self, info, id, last_name=None, other_names=None, phone=None, email_id=None):
        try:
            return InteractiveUser.objects.get(id=id)
        except InteractiveUser.DoesNotExist:
            return None

    def resolve_workforce_interactive_users(self, info, id=None, login_name=None):
        try:
            query= InteractiveUser.objects.all()

            if id:
                query= query.filter(id=id)

            if login_name:
                query= query.filter(login_name__icontains=login_name)

            return query
        except InteractiveUser.DoesNotExist:
            return None
    
    
    def resolve_workforce_eis_payment_process(
            self,
            info,
            workforce_application_id=None,
            beneficiary_id=None,
            workforce_application_tracking_number=None,
            workforce_factory_id=None,
            all_association_id=None,
            workforce_application_id_in=None,
            month=None,
            year=None,
            status=None,
            beneficiary_status=None,
            approved=None,
            approval_date_from=None,
            approval_date_to=None,
            accident_date_from=None,
            accident_date_to=None,
            not_in_stage= None
        ):
        try:
            qs = WorkforceEisPaymentProcess.objects.filter(is_deleted=False)

            if workforce_application_id:
                qs = qs.filter(workforce_application_id=workforce_application_id)

            if beneficiary_id:
                qs = qs.filter(beneficiary_id__icontains=beneficiary_id)

            if workforce_application_id_in:
                qs = qs.filter(workforce_application_id__in=workforce_application_id_in)

            if workforce_factory_id:
                qs = qs.filter(
                    workforce_application__employee_factory_id=workforce_factory_id
                )
            if workforce_application_tracking_number:
                qs = qs.filter(
                    workforce_application__tracking_number__icontains=workforce_application_tracking_number
                )
            if all_association_id:
                qs = qs.filter(
                    workforce_application__employee_factory__all_association_id=all_association_id
                )

            # if status:
            #     qs = qs.filter(status=status)
            qs = qs.filter(status="active")
            if beneficiary_status:
                qs = qs.filter(beneficiary_status=beneficiary_status)

            # if month:
            #     qs = qs.filter(month_index=month)
            #
            # if year:
            #     qs = qs.filter(year=year)

            combined_year_month_date = None

            if year and month:
                combined_year_month_date = date(int(year), int(month), 1)
            if combined_year_month_date:
                qs = qs.filter(
                    Q(remarriage_or_death_date__isnull=True) |
                    Q(remarriage_or_death_date__gt=combined_year_month_date)
                )

            if approved:
                qs = qs.filter(approved=approved)

            if approval_date_from:
                qs = qs.filter(approval_date__gte=approval_date_from)

            if approval_date_to:
                qs = qs.filter(approval_date__lte=approval_date_to)

            if accident_date_from:
                qs = qs.filter(workforce_application__accident_date__gte= accident_date_from)

            if accident_date_to:
                qs = qs.filter(workforce_application__accident_date__lte= accident_date_to)

            if not_in_stage == "yes" and year and month:
                beneficiary_ids = WorkforceEisPaymentDisbursementStage.objects.filter(
                    month_index=month,
                    year=year,
                    is_deleted=False
                ).values_list("beneficiary_id", flat=True)

                qs = qs.exclude(beneficiary_id__in=beneficiary_ids)

            qs = qs.order_by("-beneficiary_id")

            if not any([
                workforce_application_id,
                workforce_application_id_in,
                beneficiary_id,
                workforce_application_tracking_number,
                workforce_factory_id,
                all_association_id,
                month,
                year,
            ]):
                qs = qs[:500]

            return qs
        except WorkforceEisPaymentProcess.DoesNotExist:
            return None


    def resolve_workforce_eis_payment_disbursement_stage(
            self,
            info,
            month=None,
            year=None,
            workforce_factory_id= None,
            all_association_id= None,
            is_disbursed= None,
            not_in_disburse= None,
            workforce_eis_bank_advice_id= None
        ):
        try:
            qs = WorkforceEisPaymentDisbursementStage.objects.filter(is_deleted=False)

            if month:
                qs = qs.filter(month_index=month)

            if year:
                qs = qs.filter(year=year)

            if is_disbursed:
                if is_disbursed == "yes":
                    qs = qs.filter(is_disbursed=True)
                elif is_disbursed == "no":
                    qs = qs.filter(is_disbursed=False)

            if workforce_factory_id:
                qs = qs.filter(
                    workforce_application__employee_factory_id=workforce_factory_id
                )

            if all_association_id:
                qs = qs.filter(
                    workforce_application__employee_factory__all_association_id=all_association_id
                )

            if not_in_disburse == "yes" and year and month:
                beneficiary_ids = WorkforceEisPaymentDisbursement.objects.filter(
                    month_index=month,
                    year=year
                ).values_list("beneficiary_id", flat=True)
                qs = qs.exclude(beneficiary_id__in=beneficiary_ids)

            if workforce_eis_bank_advice_id:
                qs= qs.filter(workforce_eis_bank_advice_id= workforce_eis_bank_advice_id)

            qs = qs.filter(is_deleted=False)
            qs = qs.order_by("-beneficiary_id")

            if not any([
                month,
                year,
            ]):
                qs = qs[:500]

            return qs
        except WorkforceEisPaymentDisbursementStage.DoesNotExist:
            return None



    def resolve_workforce_eis_payment_disbursement(self, info, workforce_application_id=None, workforce_application_id_in=None, month=None, year=None):
        try:
            qs = WorkforceEisPaymentDisbursement.objects.filter(is_deleted=False)
            if workforce_application_id:
                qs = qs.filter(workforce_application_id=workforce_application_id)
            if workforce_application_id_in:
                qs = qs.filter(workforce_application_id__in=workforce_application_id_in)
            if month:
                qs = qs.filter(month_index=month)
            if year:
                qs = qs.filter(year=year)
            return qs
        except WorkforceEisPaymentProcess.DoesNotExist:
            return None

    def resolve_workforce_all_association(self, info, id_in=None, **kwargs):
        # if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
        #     raise PermissionDenied(_("Unauthorized access"))
        try:
            qs = WorkforceAllAssociation.objects.all()
            if id_in:
                qs = WorkforceAllAssociation.objects.filter(id__in=id_in)
            return qs
        except WorkforceAllAssociation.DoesNotExist:
            pass

    def resolve_workforce_other_compensation_info(self, info, workforce_application_id=None, **kwargs):
        try:
            if workforce_application_id:
                qs = WorkforceOtherCompensationInfo.objects.filter(workforce_application_id=workforce_application_id)
                return qs
        except WorkforceOtherCompensationInfo.DoesNotExist:
            return None

    def resolve_workforce_signatures(self, info, related_users):
        users_qs = InteractiveUser.objects.filter(id__in=related_users)
        users_map = {str(u.id): u for u in users_qs}

        # role_ids = {
        #     u.role_id for u in users_qs if u.role_id is not None
        # }
        # roles_map = {
        #     r.id: r.name
        #     for r in Role.objects.filter(id__in=role_ids)
        # }

        docs_qs = (
            WorkforceDocument.objects
            .filter(holder_id__in=related_users)
            .order_by("-date_created")
        )

        latest_docs_map = {}
        for doc in docs_qs:
            holder_key = str(doc.holder_id)
            if holder_key not in latest_docs_map:
                latest_docs_map[holder_key] = doc

        results = []

        for user_id in related_users:
            user = users_map.get(user_id)

            if not user:
                results.append({
                    "user_id": user_id,
                    "error": "User not found",
                })
                continue

            doc = latest_docs_map.get(user_id)
            user_role= UserRole.objects.filter(user_id=user_id).first() or None
            if user_role is not None:
                role_detail= Role.objects.get(id=user_role.role_id)
                results.append({
                "user_id": user_id,
                "last_name": user.last_name,
                "other_names": user.other_names,
                "role": {
                    # "id": user.role_id,
                    # "name": roles_map.
                    "id": user_role.role_id,
                    "name": role_detail.name,
                },
                "workforce_document": (
                    {
                        "id": str(doc.id),
                        "url": doc.url,
                        "path": doc.path,
                        "document_type": doc.document_type,
                        "holder_type": doc.holder_type,
                        "status": doc.status,
                    }
                    if doc else None
                ),
            })

        return results


    def resolve_workforce_association_user_map(
            self,
            info,
            all_association_id=None,
            all_association_id_in=None,
            user_id=None,
            **kwargs
    ):

        query= WorkforceAssociationUserMap.objects.filter(is_deleted=False)
        if all_association_id:
            query = query.filter(all_association_id=all_association_id)
        if all_association_id_in:
            query = query.filter(all_association_id__in=all_association_id_in)
        if user_id:
            query = query.filter(user_id=user_id)
        query = query.order_by("-date_created")
        return gql_optimizer.query(query, info)

    def resolve_workforce_eis_bank_advice(self, info, advice_date=None, is_confirmed=None, month=None, year=None):
        try:
            qs = WorkforceEisBankAdvice.objects.filter(is_deleted=False)
            if advice_date:
                qs = qs.filter(advice_date=advice_date)
            if is_confirmed:
                qs = qs.filter(is_confirmed=is_confirmed)
            if month:
                qs = qs.filter(month=month)
            if year:
                qs = qs.filter(year=year)
            return qs
        except WorkforceEisBankAdvice.DoesNotExist:
            return None

    def resolve_workforce_committees(self, info,organization_type =None,approval_type=None,**kwargs):
        service = WorkforceCommitteeServices(info.context.user)
        # query = service.get(**kwargs)
        try:
            qs = WorkforceCommittee.objects.filter(is_deleted=False)
            if organization_type:
                qs = qs.filter(organization_type=organization_type)
            if approval_type:
                qs = qs.filter(approval_type=approval_type)
            return qs
        except WorkforceCommittee.DoesNotExist:
            return None

    def resolve_workforce_committee_association_maps(self, info, **kwargs):
        service = WorkforceCommitteeAssociationMapServices(info.context.user)
        # query = service.get(**kwargs)
        try:
            qs = WorkforceCommitteeAssociationMap.objects.filter(is_deleted=False)
            return qs
        except Exception as e:
            return None

    def resolve_workforce_committee_users(self, info, **kwargs):
        service = WorkforceCommitteeUserServices(info.context.user)
        try:
            # query = service.get(**kwargs)
            # return gql_optimizer.query(query, info)
            qs= WorkforceCommitteeUser.objects.filter(is_deleted=False)
            return qs
        except Exception:
            return None

    def resolve_workforce_committee_user_maps(self, info, committee_id=None, user_id_in=None, **kwargs):
        service = WorkforceCommitteeUserMapServices(info.context.user)
        # query = service.get(**kwargs)
        try:
            qs = WorkforceCommitteeUserMap.objects.filter(is_deleted=False)
            if committee_id:
                qs = qs.filter(committee_id=committee_id)
            if user_id_in:
                qs = qs.filter(user_id__in=user_id_in)
            return qs
        except Exception as e:
            return None

    def resolve_workforce_committee_bank_advice_maps(self, info, committee_id=None, **kwargs):
        # service = WorkforceCommitteeUserMapServices(info.context.user)
        # query = service.get(**kwargs)
        try:
            qs = WorkforceCommitteeBankAdviceMap.objects.filter(is_deleted=False)
            if committee_id:
                qs = qs.filter(committee_id=committee_id)
            return qs
        except Exception as e:
            return None

    def resolve_workforce_notifications(self, info, logged_in_user_id=None, **kwargs):
        try:
            user_id= logged_in_user_id
            if not user_id:
                return WorkforceNotification.objects.none()
            
            # Get all unread notifications for the user
            unread_notifications = WorkforceNotification.objects.filter(
                user_id=user_id,
                is_read=False
            )
            
            # Get last 10 read notifications for the user
            read_notifications = WorkforceNotification.objects.filter(
                user_id=user_id,
                is_read=True
            ).order_by('-date_created')[:10]
            
            # Combine both querysets
            from django.db.models import Q
            qs = WorkforceNotification.objects.filter(
                Q(user_id=user_id, is_read=False) |
                Q(user_id=user_id, is_read=True, id__in=read_notifications.values_list('id', flat=True))
            ).order_by('-date_created')
            
            return gql_optimizer.query(qs, info)
        except Exception as e:
            return None

    def resolve_fetch_user_role_by_user_id(self, info, user_id=None, **kwargs):
        try:
            qs = UserRole.objects.filter(user_id=user_id)
            return qs
        except Exception as e:
            return None

    def resolve_fetch_noa_signature_by_approvers(self, info, user_id_in=None, **kwargs):
        try:
            user_map = WorkforceCommitteeUserMap.objects.filter(user_id__in=user_id_in).first()
            committee_id = user_map.committee_id
            noa_user = WorkforceCommitteeUserMap.objects.filter(committee_id=committee_id, is_noa_signature_user=True).first()
            noa_user_id= noa_user.user_id
            qs = WorkforceDocument.objects.filter(holder_id=noa_user_id, document_type="signature").order_by("-date_created").first()
            return qs
        except Exception as e:
            return None

    def resolve_fetch_workforce_noa_signer_user_by_approvers(self, info, user_id_in=None, **kwargs):
        try:
            user_map = WorkforceCommitteeUserMap.objects.filter(user_id__in=user_id_in).first()
            committee_id= user_map.committee_id
            qs = WorkforceCommitteeUserMap.objects.filter(committee_id=committee_id, is_noa_signature_user=True).first()
            return qs
        except Exception as e:
            return None

    def resolve_workforce_document_map(self, info, workforce_application_id=None, workforce_document_id=None, verified_by_id=None, verified_by_role_id=None, status=None, verification_date=None, **kwargs):
        try:
            qs = WorkforceDocumentMap.objects.filter(is_deleted=False)
            if workforce_application_id:
                qs = qs.filter(workforce_application_id=workforce_application_id)
            if workforce_document_id:
                qs = qs.filter(workforce_document_id=workforce_document_id)

            if verified_by_id:
                qs = qs.filter(verified_by_id=verified_by_id)

            if verified_by_role_id:
                qs = qs.filter(verified_by_role_id=verified_by_role_id)

            if status:
                qs = qs.filter(status=status)

            if verification_date:
                qs = qs.filter(verification_date= verification_date)

            return qs
        except Exception as e:
            return {"error": f"Token error: {str(e)}"}

    def resolve_website_legal_guidelines(self, info, id=None, **kwargs):
        try:
            qs= WebsiteLegalGuideline.objects.order_by("-date_created").first()
            if id:
                qs = WebsiteLegalGuideline.objects.get(id=id)
            return qs
        except Exception as e:
            return {"error": f"Token error: {str(e)}"}



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

    create_workforce_factory_registration = CreateWorkforceFactoryRegistrationMutation.Field()
    update_workforce_factory_registration = UpdateWorkforceFactoryRegistrationMutation.Field()
    approval_workforce_factory_registration = ApprovalWorkforceFactoryRegistrationMutation.Field()

    create_workforce_employer_employee = CreateWorkforceEmployeeMutation.Field()
    update_workforce_employer_employee = UpdateWorkforceEmployeeMutation.Field()

    create_workforce_document = CreateWorkforceDocumentMutation.Field()
    update_workforce_document = UpdateWorkforceDocumentMutation.Field()

    create_workforce_bank = CreateWorkforceBankMutation.Field()
    update_workforce_bank = UpdateWorkforceBankMutation.Field()

    create_workforce_employee_dependent = CreateWorkforceEmployeeDependentMutation.Field()
    update_workforce_employee_dependent = UpdateWorkforceEmployeeDependentMutation.Field()
    update_workforce_employee_dependent_eligibility = UpdateWorkforceDependentEligibilityMutation.Field()

    create_workforce_employee_designation = CreateWorkforceEmployeeDesignationMutation.Field()
    update_workforce_employee_designation = UpdateWorkforceEmployeeDesignationMutation.Field()

    create_workforce_employee_accident = CreateWorkforceEmployeeAccidentMutation.Field()
    update_workforce_employee_accident = UpdateWorkforceEmployeeAccidentMutation.Field()

    create_workforce_employee_account_info = CreateWorkforceEmployeeAccountInfoMutation.Field()
    update_workforce_employee_account_info = UpdateWorkforceEmployeeAccountInfoMutation.Field()

    create_workforce_application = CreateWorkforceApplicationMutation.Field()
    update_workforce_application = UpdateWorkforceApplicationMutation.Field()
    workforce_application_bulk_update = WorkforceApplicationBulkUpdateMutation.Field()

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

    update_workforce_interactive_user = UpdateWorkforceInteractiveUserMutation.Field()

    create_workforce_eis_payment_process = CreateWorkforceEisPaymentProcessMutation.Field()

    test_workforce_payment = TestWorkforcePaymentMutation.Field()
    # create_workforce_postoffice = CreateWorkforcePostofficeMutation.Field()
    # update_workforce_postoffice = UpdateWorkforcePostofficeMutation.Field()

    create_workforce_all_association = CreateWorkforceAllAssociationMutation.Field()
    update_workforce_all_association = UpdateWorkforceAllAssociationMutation.Field()

    create_workforce_other_compensation_info = CreateWorkforceOtherCompensationInfoMutation.Field()
    update_workforce_other_compensation_info = UpdateWorkforceOtherCompensationInfoMutation.Field()


    update_workforce_eis_payment_process_payment_type = UpdateWorkforceEisPaymentProcessPaymentTypeMutation.Field()
    update_workforce_eis_payment_process_approval = UpdateWorkforceEisPaymentProcessApprovalMutation.Field()

    update_workforce_eis_payment_by_association = UpdateWorkforceEisPaymentByAssociationMutation.Field()


    update_workforce_eis_beneficiary = UpdateWorkforceEisBeneficiaryMutation.Field()
    update_workforce_eis_beneficiary_bank = UpdateWorkforceEisBeneficiaryBankMutation.Field()

    create_workforce_eis_payment_stage = CreateWorkforceEisPaymentStageMutation.Field()
    delete_workforce_eis_payment_stage = DeleteWorkforceEisPaymentStageMutation.Field()
    create_workforce_eis_payment_disbursement = CreateWorkforceEisPaymentDisbursementMutation.Field()


    create_workforce_association_user_map = CreateWorkforceAssociationUserMapMutation.Field()
    update_workforce_association_user_map = UpdateWorkforceAssociationUserMapMutation.Field()
    delete_workforce_association_user_map = DeleteWorkforceAssociationUserMapMutation.Field()

    create_workforce_eis_bank_advice = CreateWorkforceEisBankAdviceMutation.Field()
    update_workforce_eis_bank_advice = UpdateWorkforceEisBankAdviceMutation.Field()
    revert_workforce_eis_bank_advice = RevertWorkforceEisBankAdviceMutation.Field()

    create_workforce_committee = CreateWorkforceCommitteeMutation.Field()
    update_workforce_committee = UpdateWorkforceCommitteeMutation.Field()
    delete_workforce_committee = DeleteWorkforceCommitteeMutation.Field()

    create_workforce_committee_association_map = CreateWorkforceCommitteeAssociationMapMutation.Field()
    update_workforce_committee_association_map = UpdateWorkforceCommitteeAssociationMapMutation.Field()

    create_workforce_committee_user = CreateWorkforceCommitteeUserMutation.Field()
    update_workforce_committee_user = UpdateWorkforceCommitteeUserMutation.Field()
    delete_workforce_committee_user = DeleteWorkforceCommitteeUserMutation.Field()

    create_workforce_committee_user_map = CreateWorkforceCommitteeUserMapMutation.Field()
    update_workforce_committee_user_map = UpdateWorkforceCommitteeUserMapMutation.Field()
    delete_workforce_committee_user_map = DeleteWorkforceCommitteeUserMapMutation.Field()
    update_workforce_committee_user_map_noa_signature = UpdateWorkforceCommitteeUserMapNoaSignatureMutation.Field()

    create_workforce_committee_bank_advice_map = CreateWorkforceCommitteeBankAdviceMapMutation.Field()
    update_workforce_committee_bank_advice_map = UpdateWorkforceCommitteeBankAdviceMapMutation.Field()
    delete_workforce_committee_bank_advice_map = DeleteWorkforceCommitteeBankAdviceMapMutation.Field()

    create_workforce_notification = CreateWorkforceNotificationMutation.Field()
    update_workforce_notification = UpdateWorkforceNotificationMutation.Field()

    send_sms_notification= SendSmsNotificationMutation.Field()
    create_workforce_send_confirmation_link = SendWorkforceConfirmationLinkMutation.Field()
    create_website_legal_guideline = CreateWebsiteLegalGuidelineMutation.Field()
    update_website_legal_guideline = UpdateWebsiteLegalGuidelineMutation.Field()

