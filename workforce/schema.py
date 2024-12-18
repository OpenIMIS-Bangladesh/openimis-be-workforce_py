from django.utils.translation import gettext as _
import graphene_django_optimizer as gql_optimizer
from core.schema import OrderedDjangoFilterConnectionField
from .gql_queries import *
from .gql_mutations import *


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
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_employers = OrderedDjangoFilterConnectionField(
        WorkforceEmployerGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_offices = OrderedDjangoFilterConnectionField(
        WorkforceOfficeGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )
    workforce_factories = OrderedDjangoFilterConnectionField(
        WorkforceFactoryGQLType,
        orderBy=graphene.List(of_type=graphene.String),
    )

    def resolve_workforce_representatives(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("unauthorized"))

        service = WorkforceRepresentativeServices(info.context.user)
        query = service.get(**kwargs)
        return gql_optimizer.query(query, info)

    def resolve_workforce_organizations(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("unauthorized"))
        pass

    def resolve_workforce_organization_units(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("Unauthorized access"))
        pass

    def resolve_workforce_organization_unit_designations(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("Unauthorized access"))
        pass

    def resolve_workforce_organization_employees(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("Unauthorized access"))
        pass

    def resolve_workforce_employers(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("Unauthorized access"))
        pass

    def resolve_workforce_offices(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("Unauthorized access"))
        pass

    def resolve_workforce_factories(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("Unauthorized access"))
        pass


class Mutation(graphene.ObjectType):
    create_workforce_representative = CreateWorkforceRepresentativeMutation.Field()
    create_workforce_organization = CreateWorkforceOrganizationMutation.Field()
    create_workforce_organization_unit = CreateWorkforceOrganizationUnitMutation.Field()
    create_workforce_organization_unit_designation = CreateWorkforceOrganizationUnitDesignationMutation.Field()
    create_workforce_organization_employee = CreateWorkforceOrganizationEmployeeMutation.Field()
