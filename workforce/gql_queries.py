import graphene
from django_filters import Filter
from django_filters import CharFilter
from graphene_django import DjangoObjectType
from django.contrib.postgres.fields import JSONField
from django.db.models import FileField

from core.gql_queries import InteractiveUserGQLType
from .models import (
    WorkforceRepresentative, WorkforceOrganization, WorkforceOrganizationUnit,
    WorkforceOrganizationUnitDesignation, WorkforceOrganizationEmployee,
    WorkforceEmployer, WorkforceOffice, WorkforceFactory, WorkforceEmployee, WorkforceOrganizationEmployeeDesignation,
    WorkforceDocument, Bank, WorkforceEmployeeDependent, WorkforceEmployeeDesignation, WorkforceEmployeeAccident,
    WorkforceEmployeeAccountInfo, WorkforceApplication, WorkforceDocumentType, WorkforceDocumentMap,
    WorkforceUser, WorkforceOtp, WorkforceApplicationMovement, WorkforceApplicationSummary,
    WorkforceApplicationSummaryMovement,
    WorkforceGrantMoney, WorkforceDiseases, WorkforceEducation, WorkforceEmployeeBankingInfo,
    WorkforceSignature, WorkforceFactoryRegistration, WorkforcePostoffice
)
from core import prefix_filterset, ExtendedConnection
from location.schema import LocationGQLType
import django_filters
from graphql_relay.node.node import from_global_id


class WorkforceRepresentativeGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceRepresentative
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "type": ["exact"],
            "name_bn": ["exact"],
            "name_en": ["exact"],
            "address": ["exact"],
            "phone_number": ["exact"],
            "email": ["exact"],
            "nid": ["exact"],
            "passport_no": ["exact"],
            "birth_date": ["exact"],
            "position": ["exact"],
            "status": ["exact"],
            **prefix_filterset("location__", LocationGQLType._meta.filter_fields),
            "related_user": ["exact"],
        }


class WorkforceOrganizationGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceOrganization
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "type": ["exact"],
            "name_bn": ["exact", "icontains"],
            "name_en": ["exact", "icontains"],
            "phone_number": ["exact", "icontains"],
            "email": ["exact", "icontains"],
            "address": ["icontains"],
            "status": ["exact", "isnull"],
            "parent_id": ["exact"],
            **prefix_filterset("location__", LocationGQLType._meta.filter_fields),
        }
        connection_class = ExtendedConnection


class WorkforceOrganizationEmployeeDesignationForUnitDesignationGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceOrganizationEmployeeDesignation
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "incharge_label": ["exact"],
            "status": ["exact"],
            "joining_date": ["exact"],
            "release_date": ["exact"],
            "employee_id": ["exact"]
        }
        connection_class = ExtendedConnection


class WorkforceOrganizationUnitDesignationForUnitGQLType(DjangoObjectType):
    employee_designations = graphene.List(
        WorkforceOrganizationEmployeeDesignationForUnitDesignationGQLType)
    active_employee_designation = graphene.List(
        WorkforceOrganizationEmployeeDesignationForUnitDesignationGQLType)

    class Meta:
        model = WorkforceOrganizationUnitDesignation
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "name_bn": ["exact", "icontains"],
            "name_en": ["exact", "icontains"],
            "status": ["exact", "isnull"],
            "parent": ["exact", "isnull"],
            "designation_level": ["exact"],
            "designation_sequence": ["exact"],
            **prefix_filterset("employee_designations__",
                               WorkforceOrganizationEmployeeDesignationForUnitDesignationGQLType._meta.filter_fields),
        }
        connection_class = ExtendedConnection

    def resolve_employee_designations(self, info, **kwargs):
        return WorkforceOrganizationEmployeeDesignation.objects.filter(designation_id=self.id).all()

    def resolve_active_employee_designation(self, info, **kwargs):
        return WorkforceOrganizationEmployeeDesignation.objects.filter(designation_id=self.id).filter(
            status="active").all()


class WorkforceOrganizationUnitGQLType(DjangoObjectType):
    unit_designations = graphene.List(
        WorkforceOrganizationUnitDesignationForUnitGQLType)

    class Meta:
        model = WorkforceOrganizationUnit
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "name_bn": ["exact", "icontains"],
            "name_en": ["exact", "icontains"],
            "phone_number": ["exact", "icontains"],
            "email": ["exact", "icontains"],
            "status": ["exact", "isnull"],
            "unit_level": ["exact"],
            "parent": ["exact"],
            **prefix_filterset("organization__", WorkforceOrganizationGQLType._meta.filter_fields),
            **prefix_filterset("unit_designations__",
                               WorkforceOrganizationUnitDesignationForUnitGQLType._meta.filter_fields),

        }
        connection_class = ExtendedConnection

    def resolve_unit_designations(self, info, **kwargs):
        return self.unit_designations.all()


class WorkforceOrganizationUnitDesignationGQLType(DjangoObjectType):
    employees = graphene.String()

    class Meta:
        model = WorkforceOrganizationUnitDesignation
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "name_bn": ["exact", "icontains"],
            "name_en": ["exact", "icontains"],
            "status": ["exact", "isnull"],
            "parent": ["exact", "isnull"],
            "designation_level": ["exact"],
            "designation_sequence": ["exact"],
            **prefix_filterset("organization__", WorkforceOrganizationGQLType._meta.filter_fields),
            **prefix_filterset("unit__", WorkforceOrganizationUnitGQLType._meta.filter_fields),
        }
        connection_class = ExtendedConnection

        def resolve_employees(self, info, **kwargs):
            return WorkforceOrganizationEmployeeDesignation.objects.filter(designation_id=self.id).all()


class WorkforceOrganizationEmployeeDesignationForEmployeeGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceOrganizationEmployeeDesignation
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "incharge_label": ["exact"],
            "status": ["exact"],
            "joining_date": ["exact"],
            "release_date": ["exact"],
            **prefix_filterset("designation__", WorkforceOrganizationUnitDesignationGQLType._meta.filter_fields),
        }
        connection_class = ExtendedConnection


class WorkforceOrganizationEmployeeGQLType(DjangoObjectType):
    designations = graphene.List(
        WorkforceOrganizationEmployeeDesignationForEmployeeGQLType)

    class Meta:
        model = WorkforceOrganizationEmployee
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "name_bn": ["exact", "icontains"],
            "name_en": ["exact", "icontains"],
            "gender": ["exact"],
            "address": ["exact", "icontains"],
            "phone_number": ["exact", "icontains"],
            "email": ["exact", "icontains"],
            "birth_date": ["exact"],
            "nid": ["exact"],
            "birth_certificate_no": ["exact"],
            "passport_no": ["exact"],
            "first_joining_date": ["exact"],
            "status": ["exact", "isnull"],
            "related_user": ["exact"],
            **prefix_filterset("location__", LocationGQLType._meta.filter_fields),
            **prefix_filterset("designations__",
                               WorkforceOrganizationEmployeeDesignationForEmployeeGQLType._meta.filter_fields),
        }
        connection_class = ExtendedConnection

    def resolve_designations(self, info, **kwargs):
        return self.designations.all()


class WorkforceOrganizationEmployeeDesignationGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceOrganizationEmployeeDesignation
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "incharge_label": ["exact"],
            "status": ["exact"],
            "joining_date": ["exact"],
            "release_date": ["exact"],
            **prefix_filterset("designation__", WorkforceOrganizationUnitDesignationGQLType._meta.filter_fields),
            **prefix_filterset("employee__", WorkforceOrganizationEmployeeGQLType._meta.filter_fields),
        }
        connection_class = ExtendedConnection


class WorkforceOfficeForEmployerGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceOffice
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "name_bn": ["exact", "icontains"],
            "name_en": ["exact", "icontains"],
            "address": ["exact", "icontains"],
            "phone_number": ["exact", "icontains"],
            "email": ["exact", "icontains"],
            "website": ["exact", "icontains"],
            "parent": ["exact"],
            "status": ["exact", "isnull"],
            **prefix_filterset("location__", LocationGQLType._meta.filter_fields),
            "workforce_representative": ["exact"],
            "is_same_company_representative": ["exact"],
        }
        connection_class = ExtendedConnection


class WorkforceFactoryForEmployerGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceFactory
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "employer_id": ["exact", "icontains"],
            "employer_id_lima": ["exact", "icontains"],
            "name_bn": ["exact", "icontains"],
            "name_en": ["exact", "icontains"],
            **prefix_filterset("location__", LocationGQLType._meta.filter_fields),
            "address": ["exact", "icontains"],
            "phone_number": ["exact", "icontains"],
            "email": ["exact", "icontains"],
            "website": ["exact", "icontains"],
            "status": ["exact", "isnull"],
            "workforce_representative": ["exact"],
            "is_same_company_representative": ["exact"],
        }
        connection_class = ExtendedConnection


class WorkforceEmployerGQLType(DjangoObjectType):
    office_count = graphene.Int()
    factory_count = graphene.Int()

    offices = graphene.List(WorkforceOfficeForEmployerGQLType)
    factories = graphene.List(WorkforceFactoryForEmployerGQLType)

    class Meta:
        model = WorkforceEmployer
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "employer_id": ["exact", "icontains"],
            "employer_id_lima": ["exact", "icontains"],
            "name_bn": ["exact", "icontains"],
            "name_en": ["exact", "icontains"],
            "address": ["exact", "icontains"],
            "phone_number": ["exact", "icontains"],
            "email": ["exact", "icontains"],
            "website": ["exact", "icontains"],
            "licence_type": ['exact'],
            "licence_number": ['exact'],
            "business_sector": ['exact'],
            "foundation_date": ['exact'],
            "association_name": ['exact'],
            "association_membership_number": ['exact'],
            "establishment_Name": ['exact'],
            "establishment_date": ['exact'],
            "status": ["exact", "isnull"],
            **prefix_filterset("location__", LocationGQLType._meta.filter_fields),
            "workforce_representative": ["exact"],
        }
        connection_class = ExtendedConnection

    def resolve_offices(self, info):
        return WorkforceOffice.objects.filter(workforce_employer=self.id).all()

    def resolve_factories(self, info):
        return WorkforceFactory.objects.filter(workforce_employer=self.id).all()

    def resolve_office_count(self, info):
        return WorkforceOffice.objects.filter(workforce_employer=self.id).count()

    def resolve_factory_count(self, info):
        return WorkforceFactory.objects.filter(workforce_employer=self.id).count()


class WorkforceOfficeGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceOffice
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "workforce_employer": ["exact"],
            "name_bn": ["exact", "icontains"],
            "name_en": ["exact", "icontains"],
            "address": ["exact", "icontains"],
            "phone_number": ["exact", "icontains"],
            "email": ["exact", "icontains"],
            "website": ["exact", "icontains"],
            "parent": ["exact"],
            "status": ["exact", "isnull"],
            **prefix_filterset("location__", LocationGQLType._meta.filter_fields),
            "workforce_representative": ["exact"],
            "is_same_company_representative": ["exact"],
        }
        connection_class = ExtendedConnection


class WorkforceFactoryGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceFactory
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "workforce_employer_id": ["exact"],
            "employer_id": ["exact", "icontains"],
            "employer_id_lima": ["exact", "icontains"],
            "name_bn": ["exact", "icontains"],
            "name_en": ["exact", "icontains"],
            **prefix_filterset("location__", LocationGQLType._meta.filter_fields),
            "address": ["exact", "icontains"],
            "phone_number": ["exact", "icontains"],
            "email": ["exact", "icontains"],
            "website": ["exact", "icontains"],
            "status": ["exact", "isnull"],
            "workforce_representative_id": ["exact"],
            "association_type": ["exact"],
            "is_same_company_representative": ["exact"],
        }
        connection_class = ExtendedConnection


class WorkforceEmployeeGQLType(DjangoObjectType):
    join_date = graphene.String()
    resignation_date = graphene.String()
    resignation_reason = graphene.String()
    monthly_salary = graphene.String()
    position = graphene.String()
    workforce_company_id = graphene.String()
    workforce_factory_id = graphene.String()
    workforce_office_id = graphene.String()

    class Meta:
        model = WorkforceEmployee
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "employee_id": ["exact"],
            "employee_id_lima": ["exact"],
            "insurance_number": ["exact"],
            "employee_type": ["exact"],
            "global_id": ["exact"],
            "first_name_bn": ["exact"],
            "last_name_bn": ["exact"],
            "other_name": ["exact"],
            "first_name_en": ["exact"],
            "last_name_en": ["exact"],
            "father_name_bn": ["exact"],
            "father_name_en": ["exact"],
            "mother_name_bn": ["exact"],
            "mother_name_en": ["exact"],
            "spouse_name_bn": ["exact"],
            "spouse_name_en": ["exact"],
            "citizenship": ["exact"],
            "privacy_law": ["exact"],
            "marital_status": ["exact"],
            "gender": ["exact"],
            "photo_path": ["exact"],
            "photo_date": ["exact"],
            "position": ["exact"],
            "monthly_earning": ["exact"],
            "reference_salary": ["exact"],
            "present_address": ["exact"],
            "permanent_address": ["exact"],
            "phone_number": ["exact"],
            "email": ["exact"],
            "birth_date": ["exact"],
            "nid": ["exact"],
            "birth_certificate_no": ["exact"],
            "passport_no": ["exact"],
            "registration_date": ["exact"],
            "life_status": ["exact", "icontains"],
            "disability_status": ["exact", "icontains"],
            "death_date": ["icontains"],
            "status": ["exact"],
            **prefix_filterset("related_user__", InteractiveUserGQLType._meta.filter_fields),
            **prefix_filterset("present_location__", LocationGQLType._meta.filter_fields),
            **prefix_filterset("permanent_location__", LocationGQLType._meta.filter_fields),
        }
        connection_class = ExtendedConnection

        def resolve_join_dates(self, info):
            return WorkforceEmployeeDesignation.objects.filter(
                workforce_employee_id=self.id,
                status__iexact='active'
            ).order_by('-id').first()

        def resolve_resignation_dates(self, info):
            return WorkforceEmployeeDesignation.objects.filter(
                workforce_employee_id=self.id,
                status__iexact='active'
            ).order_by('-id').first()

        def resolve_resignation_reasons(self, info):
            return WorkforceEmployeeDesignation.objects.filter(
                workforce_employee_id=self.id,
                status__iexact='active'
            ).order_by('-id').first()

        def resolve_monthly_salary(self, info):
            return WorkforceEmployeeDesignation.objects.filter(
                workforce_employee_id=self.id,
                status__iexact='active'
            ).order_by('-id').first()

        def resolve_positions(self, info):
            return WorkforceEmployeeDesignation.objects.filter(
                workforce_employee_id=self.id,
                status__iexact='active'
            ).order_by('-id').first()

        def resolve_workforce_company_ids(self, info):
            return WorkforceEmployeeDesignation.objects.filter(
                workforce_employee_id=self.id,
                status__iexact='active'
            ).order_by('-id').first()

        def resolve_workforce_office_ids(self, info):
            return WorkforceEmployeeDesignation.objects.filter(
                workforce_employee_id=self.id,
                status__iexact='active'
            ).order_by('-id').first()

        def resolve_workforce_factory_ids(self, info):
            return WorkforceEmployeeDesignation.objects.filter(
                workforce_employee_id=self.id,
                status__iexact='active'
            ).order_by('-id').first()


class WorkforceApplicationSummaryGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceApplicationSummary
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "application_data": [],
            "meeting_date": ["exact"],
            "remarks": [],
            "name": ["exact"],
            "status": ["exact"],
            "organization_type": ["exact"],
            "section_type": ["exact"],
            "year": ["exact"],
            "month": ["exact"],
        }
        connection_class = ExtendedConnection


class WorkforceApplicationGQLType(DjangoObjectType):
    workforce_employee = graphene.Field(lambda: WorkforceEmployeeGQLType)
    workforce_application_movement = graphene.Field(lambda: WorkforceApplicationMovementGQLType)
    workforce_application_movements = graphene.List(lambda: WorkforceApplicationMovementGQLType)

    class Meta:
        model = WorkforceApplication
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "employee_designation_info": [],
            "employee_document_info": [],
            "employee_bank_info": [],
            "employee_dependent_info": [],
            "employee_accident_info": [],
            "employee_children_info": [],
            "applicant_info": [],
            "organization_id": ["exact"],
            "organization_type": ["exact"],
            "employee_employer_id": ["exact"],
            "employee_factory_id": ["exact"],
            "application_type": ["exact"],
            "association_type": ["exact"],
            "is_submitted": ["exact"],
            "phone_number": ["exact"],
            "tracking_number": ["exact"],
            **prefix_filterset("workforce_employee__", WorkforceEmployeeGQLType._meta.filter_fields),
            **prefix_filterset("cf_application_summary__", WorkforceApplicationSummaryGQLType._meta.filter_fields),
            **prefix_filterset("eis_application_summary__", WorkforceApplicationSummaryGQLType._meta.filter_fields),
            **prefix_filterset("blwf_application_summary__", WorkforceApplicationSummaryGQLType._meta.filter_fields),
            "grant_money_id": ["exact"],
            "metadata": [],
            "grant_amount": ["exact"],
            "submitted_by": ["exact"],
            "status": ["exact"],
            # enable filtering by fields on WorkforceApplicationMovement via reverse FK
            "application__application_to_id": ["exact"],
        }
        connection_class = ExtendedConnection

    def resolve_workforce_employee(self, info):
        return self.workforce_employee

    def resolve_workforce_application_movement(self, info, **kwargs):
        return WorkforceApplicationMovement.objects.filter(
            application_id=self.id, is_current=True
        ).first()

    def resolve_workforce_application_movements(self, info, **kwargs):
        return WorkforceApplicationMovement.objects.filter(
            application_id=self.id
        ).order_by("-id")


class WorkforceEmployeeDesignationGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceEmployeeDesignation
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "workforce_application_id": ['exact'],
            "id": ["exact"],
            "workforce_employee_id": ["exact"],
            "workforce_company_id": ["exact"],
            "workforce_factory_id": ["exact"],
            "workforce_office_id": ["exact"],
            "position": ["exact"],
            "join_date": ["exact"],
            "resignation_date": ["exact"],
            "resignation_reason": ["exact", "icontains"],
            "monthly_salary": ["exact"],
            "status": ["exact", "icontains"],
            **prefix_filterset("workforce_employee__", {
                "email": ["exact"],
                "nid": ["exact", "icontains"],
            }),
        }
        connection_class = ExtendedConnection


class WorkforceBankGQLType(DjangoObjectType):
    class Meta:
        model = Bank
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "name_en": ["exact", "icontains"],
            "name_bn": ["exact", "icontains"],
            "bank_code": ["exact", "icontains"],
            "branch_code": ["exact", "icontains"],
            "district_code": ["exact", "icontains"],
            "district_name_en": ["exact", "icontains"],
            "district_name_bn": ["exact", "icontains"],
            "routing_number": ["exact"],
            "parent": ["exact"],
            "contact_number": ["exact"],
            "type": ["exact"],
            "status": ["exact", "icontains"],
        }
        connection_class = ExtendedConnection


class WorkforceEmployeeDependentGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceEmployeeDependent
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            **prefix_filterset("workforce_application__", WorkforceApplicationGQLType._meta.filter_fields),
            "eis_insurance_no": ["exact"],
            "name_en": ["exact", "icontains"],
            "name_bn": ["exact", "icontains"],
            "father_name_bn": ["exact", "icontains"],
            "father_name_en": ["exact", "icontains"],
            "mother_name_bn": ["exact", "icontains"],
            "mother_name_en": ["exact", "icontains"],
            "marital_status": ["exact"],
            "gender": ["exact"],
            "occupation": ["exact", "icontains"],
            "email": ["exact"],
            "phone_number": ["exact"],
            "birth_date": ["exact"],
            "nid": ["exact"],
            "birth_certificate_no": ["exact"],
            "present_address": ["exact", "icontains"],
            "permanent_address": ["exact", "icontains"],
            "life_status": ["exact", "icontains"],
            "death_date": ["exact"],
            "disability_status": ["exact", "icontains"],
            "relation_with_worker": ["exact", "icontains"],
            "last_verification_date": ["exact"],
            "status": ["exact", "icontains"],
            "percentage_of_cf_grant": ["exact"],
            **prefix_filterset("present_location__", LocationGQLType._meta.filter_fields),
            **prefix_filterset("permanent_location__", LocationGQLType._meta.filter_fields),
        }
        connection_class = ExtendedConnection


class WorkforceEmployeeAccidentGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceEmployeeAccident
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "workforce_application_id": ['exact'],
            "employee_id": ["exact"],
            "injury_type": ["exact", "contains"],
            "accident_date": ["exact"],
            "accident_time": ["exact"],
            "accident_type": ["exact", "contains"],
            "duty_status": ["exact", "contains"],
            "in_outside_factory": ["exact", "contains"],
            "death_date": ["exact"],
            "description": ["exact", "contains"],
            "accident_location": ["exact"],
            "rejoin_date": ["exact"],
            "status": ["exact", "icontains"],
        }
        connection_class = ExtendedConnection


class WorkforceEmployeeAccountInfoGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceEmployeeAccountInfo
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "beneficiary_type": ["exact"],
            "beneficiary_id": ["exact"],
            "on_behalf_of": ["exact", "contains"],
            "present_location_id": ["exact"],
            "permanent_location_id": ["exact"],
            "bank_id": ["exact"],
            "branch_id": ["exact"],
            "account_holder_name": ["exact", "contains"],
            "account_owner_name": ["exact", "contains"],
            "account_number": ["exact", "contains"],
            "status": ["exact", "icontains"],
            **prefix_filterset("present_location__", LocationGQLType._meta.filter_fields),
            **prefix_filterset("permanent_location__", LocationGQLType._meta.filter_fields),
        }
        connection_class = ExtendedConnection


class WorkforceDocumentGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceDocument
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection
        filter_fields = {
            "id": ["exact"],
            "workforce_application_id": ["exact"],
            "holder": ["exact"],
            "holder_type": ["exact", "icontains"],
            "verifier_id": ["exact"],
            "approver_id": ["exact"],
            "factory_id": ["exact"],
            "workforce_document_type_id": ["exact"],
            "workforce_dependent_id": ["exact"],
            "note": ["exact", "icontains"],
            "document_type": ["exact", "icontains"],
            "path": ["exact"],
            "url": ["exact"],
            "submission_date": ["exact"],
            "verification_date": ["exact"],
            "approval_date": ["exact"],
            "remarks": ["exact", "icontains"],
            "status": ["exact", "icontains"],
            **prefix_filterset("workforce_application__", WorkforceApplicationGQLType._meta.filter_fields),
        }


class WorkforceDocumentTypeGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceDocumentType
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "field_id": ["exact"],
            "document_type": ["exact"],
            "application_type": ["exact"],
            "organization_type": ["exact"],
            "application_for": ["exact"],
            "document_type_no": ["exact"],
            "document_count": ["exact"],
            "name_bn": ["exact", "contains"],
            "name_en": ["exact", "contains"],
            "workforce_disease": ["exact"],
            "mandatory_for_applicant": ["exact"],
            "form_step_no": ["exact"],
            "status": ["exact"],
        }
        connection_class = ExtendedConnection


class WorkforceDocumentMapGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceDocumentMap
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "workforce_document_type_id": ["exact"],
            "mapped_by_id": ["exact"],
            "type": ["contains"],
            "status": ["exact"],
        }
        connection_class = ExtendedConnection


class WorkforceUserGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceUser
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "name_bn": ["exact", "contains"],
            "first_name_en": ["exact", "contains"],
            "last_name_en": ["exact", "contains"],
            "nid": ["exact", "contains"],
            "birth_certificate_no": ["exact"],
            "phone_number": ["exact"],
            "status": ["exact"],
        }
        connection_class = ExtendedConnection


class WorkforceOtpGQLType(graphene.ObjectType):
    status = graphene.String()
    name_bn = graphene.String()
    first_name_en = graphene.String()
    nid = graphene.String()
    birth_certificate_no = graphene.String()
    phone_number = graphene.String()


class WorkforceApplicationMovementFilter(django_filters.FilterSet):
    application_to_id = django_filters.CharFilter(method="filter_application_to_id")

    def filter_application_to_id(self, queryset, name, value):
        if not value:
            return queryset
        v = value.strip()
        if v.isdigit():
            return queryset.filter(**{name: int(v)})
        try:
            _, dbid = from_global_id(v)
            return queryset.filter(**{name: int(dbid)})
        except Exception:
            return queryset.none()

    class Meta:
        model = WorkforceApplicationMovement
        fields = {
            "id": ["exact"],
            "application_id": ["exact"],
            "note": ["exact", "contains"],
            "action": ["exact", "contains"],
            "to_employee_record_id": ["exact"],
            "from_employee_record_id": ["exact"],
            "to_office_unit_organogram_id": ["exact"],
            "from_office_unit_organogram_id": ["exact"],
            "to_office_id": ["exact"],
            "from_office_id": ["exact"],
            "to_office_unit_id": ["exact"],
            "from_office_unit_id": ["exact"],
            "is_current": ["exact"],
            "is_cc": ["exact"],
            "is_committee_head": ["exact"],
            "is_committee_member": ["exact"],
            "to_employee_name_bng": ["exact", "contains"],
            "from_employee_name_bng": ["exact", "contains"],
            "to_employee_name_eng": ["exact", "contains"],
            "from_employee_name_eng": ["exact", "contains"],
            "to_employee_designation_bng": ["exact", "contains"],
            "from_employee_designation_bng": ["exact", "contains"],
            "to_office_name_bng": ["exact", "contains"],
            "from_office_name_bng": ["exact", "contains"],
            "to_employee_unit_name_bng": ["exact", "contains"],
            "from_employee_unit_name_bng": ["exact", "contains"],
            "from_employee_username": ["exact", "contains"],
            "application_from_id": ["exact"],
            "application_to_id": ["exact"],
            "deadline_date": ["exact"],
            "is_reverted": ["exact"],
            "reverting_date": ["exact"],
            "reverted_by": ["exact"],
            "revert_note": ["exact"],
            "status": ["exact", "icontains"],
        }


class WorkforceApplicationMovementGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceApplicationMovement
        interfaces = (graphene.relay.Node,)
        filterset_class = WorkforceApplicationMovementFilter
        connection_class = ExtendedConnection


class WorkforceApplicationSummaryMovementGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceApplicationSummaryMovement
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "application_summary_id": [],
            "comment": [],
            "action": ["exact"],
            "from_workforce_organization_employee_id": ["exact"],
            "to_workforce_organization_employee_id": ["exact"],
            "is_current": ["exact"],
            "is_cc": ["exact"],
            "is_committee_head": ["exact"],
            "is_committee_member": ["exact"],
            "deadline_date": ["exact"],
            "is_reverted": ["exact"],
            "reverting_date": ["exact"],
            "reverted_by_id": ["exact"],
            "revert_note": [],
            "status": ["exact"],
        }
        connection_class = ExtendedConnection


class WorkforceGrantMoneyGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceGrantMoney
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "organization_type": ["exact"],
            "application_type": ["exact"],
            "application_type_name_bn": ["exact"],
            "application_type_name_en": ["exact"],
            "grant_money": ["exact"],
            "application_type_no": ["exact"],
            "status": ["exact"],
        }
        connection_class = ExtendedConnection


class WorkforceDiseasesGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceDiseases
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "grade": ["exact"],
            "disease_type": ["exact"],
            "disease_name": ["exact"],
            "disease_no": ["exact"],
            "documents": [],
            "minimum_donation_amount": ["exact"],
            "maximum_donation_amount": ["exact"],
            "status": ["exact"],
        }
        connection_class = ExtendedConnection


class WorkforceEducationGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceEducation
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            **prefix_filterset("application__", WorkforceApplicationGQLType._meta.filter_fields),
            "workforce_employee": ["exact"],
            "workforce_dependant": ["exact"],
            "education_level": ["exact", "icontains"],
            "applicant_type": ["exact", "icontains"],
            "education_board": ["exact", "icontains"],
            "passing_year": ["exact"],
            "roll_number": ["exact", "icontains"],
            "registration_number": ["exact", "icontains"],
            "result": ["exact", "gte", "lte"],
            "institution": ["exact", "icontains"],
            "child_name_en": ["exact", "icontains"],
            "child_name_bn": ["exact", "icontains"],
            "child_birth_date": ["exact", "icontains"],
            "child_nid_no": ["exact", "icontains"],
            "child_birth_certificate_no": ["exact", "icontains"],
            "study_class": ["exact", "icontains"],
        }
        connection_class = ExtendedConnection


class WorkforceEmployeeBankingInfoGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceEmployeeBankingInfo
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "name_bn": ["exact", "icontains"],
            "name_en": ["exact", "icontains"],
            "account_holder_name": ["exact", "icontains"],
            "employee_id": ["exact"],
            "application_id": ["exact"],
            "dependant_id": ["exact"],
            "bank_id": ["exact"],
            "type": ["exact", "icontains"],
            "amount": ["exact", "icontains"],
            "account_no": ["exact", "icontains"],
            "status": ["exact"],
        }
        connection_class = ExtendedConnection


class WorkforceSignatureGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceSignature
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "related_user_id": ["exact"],
            "path": ["exact"],
            "url": ["exact"],
            "status": ["exact"],
        }
        connection_class = ExtendedConnection


class WorkforceFactoryRegistrationGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceFactoryRegistration
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "factory_id": ['exact'],
            "name_bn": ['exact'],
            "name_en": ['exact'],
            "location": ['exact'],
            "address": ['exact'],
            "phone_number": ['exact'],
            "email": ['exact'],
            "website": ['exact'],
            "status": ['exact'],
            "association_type": ['exact'],
            "representative_type": ['exact'],
            "representative_name_bn": ['exact'],
            "representative_name_en": ['exact'],
            "representative_location": ['exact'],
            "representative_address": ['exact'],
            "representative_phone_number": ['exact'],
            "representative_email": ['exact'],
            "representative_nid": ['exact'],
            "representative_passport_no": ['exact'],
            "representative_birth_date": ['exact'],
            "representative_position": ['exact'],
            "approval_status": ['exact']
        }
        connection_class = ExtendedConnection


class WorkforcePostofficeGQLType(graphene.ObjectType):
    id = graphene.String()
    w_code = graphene.String(required=True)
    post_code = graphene.String()
    post_office = graphene.String()
    name_en = graphene.String()
    name_bn = graphene.String()
    status = graphene.String()


class WorkforceUserRoleGQLType(graphene.ObjectType):
    id = graphene.String()
    role_id = graphene.String()
    user_id = graphene.String()
    last_name = graphene.String()
    other_names = graphene.String()