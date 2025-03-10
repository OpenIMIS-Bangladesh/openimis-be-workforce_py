import graphene
from django_filters import Filter
from django_filters import CharFilter
from graphene_django import DjangoObjectType
from django.contrib.postgres.fields import JSONField
from .models import (
    WorkforceRepresentative, WorkforceOrganization, WorkforceOrganizationUnit,
    WorkforceOrganizationUnitDesignation, WorkforceOrganizationEmployee,
    WorkforceEmployer, WorkforceOffice, WorkforceFactory, WorkforceEmployee, WorkforceOrganizationEmployeeDesignation,
    WorkforceDocument, Bank, WorkforceEmployeeDependent, WorkforceEmployeeDesignation, WorkforceEmployeeAccident,
    WorkforceEmployeeAccountInfo, WorkforceApplication
)
from core import prefix_filterset, ExtendedConnection
from location.schema import LocationGQLType


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
        }
        connection_class = ExtendedConnection


class WorkforceOrganizationUnitDesignationForUnitGQLType(DjangoObjectType):
    employee_designations = graphene.List(WorkforceOrganizationEmployeeDesignationForUnitDesignationGQLType)
    active_employee_designation = graphene.List(WorkforceOrganizationEmployeeDesignationForUnitDesignationGQLType)

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
    unit_designations = graphene.List(WorkforceOrganizationUnitDesignationForUnitGQLType)

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
    designations = graphene.List(WorkforceOrganizationEmployeeDesignationForEmployeeGQLType)

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
            "workforce_employer": ["exact"],
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
            "related_user_id": ["exact"],
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


class WorkforceEmployeeDesignationGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceEmployeeDesignation
        interfaces = (graphene.relay.Node,)
        filter_fields = {
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
        }
        connection_class = ExtendedConnection


class WorkforceDocumentGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceDocument
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "holder": ["exact"],
            "holder_type": ["exact", "icontains"],
            "verifier": ["exact"],
            "approver": ["exact"],
            "document_type": ["exact", "icontains"],
            "path": ["exact"],
            "submission_date": ["exact"],
            "verification_date": ["exact"],
            "approval_date": ["exact"],
            "remarks": ["exact", "icontains"],
            "status": ["exact", "icontains"],
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
            "parent": ["exact"],
            "headquarter_address": ["exact", "icontains"],
            "location": ["exact"],
            "type": ["exact"],
            "routing_number": ["exact"],
            "contact_number": ["exact"],
            "status": ["exact", "icontains"],
        }
        connection_class = ExtendedConnection


class WorkforceEmployeeDependentGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceEmployeeDependent
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "eis_insurance_no": ["exact"],
            "first_name_bn": ["exact", "icontains"],
            "last_name_bn": ["exact", "icontains"],
            "first_name_en": ["exact", "icontains"],
            "last_name_en": ["exact", "icontains"],
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
            "present_location_id": ["exact"],
            "permanent_location_id": ["exact"],
            "present_address": ["exact", "icontains"],
            "permanent_address": ["exact", "icontains"],
            "life_status": ["exact", "icontains"],
            "death_date": ["exact"],
            "disability_status": ["exact", "icontains"],
            "relation_type": ["exact", "icontains"],
            "relation_with_worker": ["exact", "icontains"],
            "last_verification_date": ["exact"],
            "status": ["exact", "icontains"],
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
            "account_holder_name": ["exact", "contains"],
            "account_number": ["exact", "contains"],
            "status": ["exact", "icontains"],
            **prefix_filterset("present_location__", LocationGQLType._meta.filter_fields),
            **prefix_filterset("permanent_location__", LocationGQLType._meta.filter_fields),
        }
        connection_class = ExtendedConnection


class WorkforceApplicationGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceApplication
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
            "related_user_id": ["exact"],
            "employee_designation_info": [],
            "employee_document_info": [],
            "employee_bank_info": [],
            "employee_dependent_info": [],
            "employee_accident_info": [],
            "status": ["exact"],
            **prefix_filterset("present_location__", LocationGQLType._meta.filter_fields),
            **prefix_filterset("permanent_location__", LocationGQLType._meta.filter_fields),
        }
        connection_class = ExtendedConnection
