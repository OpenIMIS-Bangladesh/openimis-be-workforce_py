import graphene


class WorkforceRepresentativeInputType:
    type = graphene.String(requred=True)
    name_bn = graphene.String(required=True)
    name_en = graphene.String(required=True)
    location = graphene.Int(required=True)
    address = graphene.String(required=True)
    phone_number = graphene.String()
    email = graphene.String()
    nid = graphene.String()
    passport_no = graphene.String()
    birth_date = graphene.String(required=True)
    position = graphene.String(required=True)
    status = graphene.Boolean()
    user_id = graphene.Int()


class WorkforceOrganizationInputType:
    name_bn = graphene.String()
    name_en = graphene.String(required=True)
    location = graphene.Int(required=True)
    address = graphene.String()
    phone_number = graphene.String()
    email = graphene.String()
    website = graphene.String()
    status = graphene.Boolean()
    parent_id = graphene.Int()
    workforce_representative_id = graphene.UUID(required=True)


class WorkforceOrganizationUnitInputType:
    unit_level = graphene.Int(required=True)
    name_bn = graphene.String()
    name_en = graphene.String(required=True)
    phone_number = graphene.String()
    email = graphene.String()
    status = graphene.Boolean()
