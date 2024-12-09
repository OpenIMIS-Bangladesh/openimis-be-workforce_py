import graphene
from graphene_django import DjangoObjectType

from .apps import WorkforceConfig
from .models import (
    WorkforceRepresentative, WorkforceOrganization, WorkforceOrganizationUnit,
    WorkforceOrganizationUnitDesignation, WorkforceOrganizationEmployee,
    WorkforceEmployer, WorkforceOffice, WorkforceFactory, WorkforceEmployee
)
from core import prefix_filterset, ExtendedConnection
from django.utils.translation import gettext as _
from django.core.exceptions import PermissionDenied
from contribution.schema import PremiumGQLType


class WorkforceOrganizationGQLType(DjangoObjectType):
    client_mutation_id = graphene.String()

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
            # "location_id": ["exact"],
            # "workforce_representative_id": ["exact"],
            "status": ["exact", "isnull"],
        }
        connection_class = ExtendedConnection

    def resolve_client_mutation_id(self, info):
        if not info.context.user.has_perms(WorkforceConfig.gql_query_workforces_perms):
            raise PermissionDenied(_("unauthorized"))
        payment_mutation = self.mutations.select_related(
            'mutation').filter(mutation__status=0).first()
        return payment_mutation.mutation.client_mutation_id if payment_mutation else None

