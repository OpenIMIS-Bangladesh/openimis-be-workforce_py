import graphene
from graphene_django import DjangoObjectType

from .models import (
    WorkforceRepresentative, WorkforceOrganization, WorkforceOrganizationUnit,
    WorkforceOrganizationUnitDesignation, WorkforceOrganizationEmployee,
    WorkforceEmployer, WorkforceOffice, WorkforceFactory, WorkforceEmployee, WorkforceOrganizationEmployeeDesignation,
    WorkforceDocument,
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


class WorkforceEmployerGQLType(DjangoObjectType):
    office_count = graphene.Int()
    factory_count = graphene.Int()

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
    class Meta:
        model = WorkforceEmployee
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "employee_id": ["exact"],
            "employee_id_lima": ["exact"],
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
            "status": ["exact"],
            **prefix_filterset("present_location__", LocationGQLType._meta.filter_fields),
            **prefix_filterset("permanent_location__", LocationGQLType._meta.filter_fields),
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
