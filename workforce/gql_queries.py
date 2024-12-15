import graphene
from graphene_django import DjangoObjectType

from .models import (
    WorkforceRepresentative, WorkforceOrganization, WorkforceOrganizationUnit,
    WorkforceOrganizationUnitDesignation, WorkforceOrganizationEmployee,
    WorkforceEmployer, WorkforceOffice, WorkforceFactory, WorkforceEmployee
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
            "organization": ["exact"],
            "name_bn": ["exact", "icontains"],
            "name_en": ["exact", "icontains"],
            "phone_number": ["exact", "icontains"],
            "email": ["exact", "icontains"],
            "status": ["exact", "isnull"],
            "unit_level": ["exact"],
            "parent": ["exact"],
            "workforce_representative": ["exact"],
        }
        connection_class = ExtendedConnection


class WorkforceOrganizationUnitDesignationGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceOrganizationUnitDesignation
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "organization": ["exact"],
            "unit": ["exact"],
            "name_bn": ["exact", "icontains"],
            "name_en": ["exact", "icontains"],
            "status": ["exact", "isnull"],
            "parent": ["exact", "isnull"],
            "designation_level": ["exact"],
            "designation_sequence": ["exact"],
        }
        connection_class = ExtendedConnection


class WorkforceOrganizationEmployeeGQLType(DjangoObjectType):
    class Meta:
        model = WorkforceOrganizationEmployee
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "designation": ["exact"],
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
            "status": ["exact", "isnull"],
            "related_user": ["exact"],
            **prefix_filterset("location__", LocationGQLType._meta.filter_fields),  # Using Location filter fields
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
            **prefix_filterset("location__", LocationGQLType._meta.filter_fields),  # Using Location filter fields
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
            **prefix_filterset("location__", LocationGQLType._meta.filter_fields),  # Using Location filter fields
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
            **prefix_filterset("location__", LocationGQLType._meta.filter_fields),  # Using Location filter fields
            "address": ["exact", "icontains"],
            "phone_number": ["exact", "icontains"],
            "email": ["exact", "icontains"],
            "website": ["exact", "icontains"],
            "status": ["exact", "isnull"],
            "workforce_representative": ["exact"],
        }
        connection_class = ExtendedConnection
