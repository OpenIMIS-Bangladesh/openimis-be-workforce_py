from django.utils.translation import gettext as _
from core.schema import signal_mutation_module_before_mutating, OrderedDjangoFilterConnectionField, filter_validity
from .gql_queries import *
from .gql_mutations import *


class Query(graphene.ObjectType):
    workforce_organizations = OrderedDjangoFilterConnectionField(
        WorkforceOrganizationGQLType,
    )

    def resolve_workforce_organizations(self, info, **kwargs):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("unauthorized"))
        pass


class Mutation(graphene.ObjectType):
    create_workforce_representative = CreateWorkforceRepresentativeMutation.Field()
    create_workforce_organization = CreateWorkforceOrganizationMutation.Field()
