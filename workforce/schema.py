import graphene
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from graphene_django.filter import DjangoFilterConnectionField
import graphene_django_optimizer as gql_optimizer
from .apps import WorkforceConfig
from django.utils.translation import gettext as _
from core.schema import signal_mutation_module_before_mutating, OrderedDjangoFilterConnectionField, filter_validity
from core.services import wait_for_mutation
from contribution import models as contribution_models

# We do need all queries and mutations in the namespace here.
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
    create_workforce_organization = CreateWorkforceOrganizationMutation.Field()
