import graphene
from graphene_django import DjangoObjectType

from .models import (
    WorkforceRepresentative, WorkforceOrganization, WorkforceOrganizationUnit,
    WorkforceOrganizationUnitDesignation, WorkforceOrganizationEmployee,
    WorkforceEmployer, WorkforceOffice, WorkforceFactory, WorkforceEmployee, WorkforceOrganizationEmployeeDesignation
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


class WorkforceOrganizationUnitGQLType(DjangoObjectType):
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

        }
        connection_class = ExtendedConnection


class WorkforceOrganizationUnitDesignationGQLType(DjangoObjectType):
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
            **prefix_filterset("designations__", WorkforceOrganizationEmployeeDesignationForEmployeeGQLType._meta.filter_fields),
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
        }
        connection_class = ExtendedConnection


class WorkforceEmployeeGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceEmployee
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "workforce_employer": ["exact"],
            "workforce_office": ["exact"],
            "workforce_factory": ["exact"],
            "employee_id": ["exact", "icontains"],
            "employee_type": ["exact"],
            "global_id": ["exact", "icontains"],
            "present_location": ["exact"],
            "permanent_location": ["exact"],
            "name_bn": ["exact", "icontains"],
            "name_en": ["exact", "icontains"],
            "fathers_name": ["exact", "icontains"],
            "mothers_name": ["exact", "icontains"],
            "gender": ["exact", "icontains"],
            "marital_status": ["exact", "icontains"],
            "photo_path": ["exact", "icontains"],
            "photo_date": ["exact", "icontains"],
            "position": ["exact", "icontains"],
            "monthly_earning": ["exact", "icontains"],
            "reference_salary": ["exact", "icontains"],
            "present_address": ["exact", "icontains"],
            "permanent_address": ["exact", "icontains"],
            "phone_number": ["exact", "icontains"],
            "email": ["exact", "icontains"],
            "birth_date": ["exact", "icontains"],
            "nid": ["exact", "icontains"],
            "birth_certificate_no": ["exact", "icontains"],
            "passport_no": ["exact", "icontains"],
            "status": ["exact", "icontains"],
            "related_user": ["exact"],
            **prefix_filterset("location__", LocationGQLType._meta.filter_fields),
        }
        connection_class = ExtendedConnection