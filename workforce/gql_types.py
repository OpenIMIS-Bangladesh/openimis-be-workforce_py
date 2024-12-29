import graphene

from core.schema import OpenIMISMutation


class WorkforceRepresentativeInputType(OpenIMISMutation.Input):
    type = graphene.String(requred=True)
    name_bn = graphene.String(required=True)
    name_en = graphene.String(required=True)
    location = graphene.String(required=True)
    address = graphene.String(required=True)
    phone_number = graphene.String()
    email = graphene.String()
    nid = graphene.String()
    passport_no = graphene.String()
    birth_date = graphene.String(required=True)
    position = graphene.String(required=True)
    status = graphene.Boolean()
    user_id = graphene.String()


class WorkforceOrganizationInputType(OpenIMISMutation.Input):
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


class WorkforceOrganizationUnitInputType(OpenIMISMutation.Input):
    organization = graphene.UUID(required=True)
    unit_level = graphene.Int()
    name_bn = graphene.String()
    name_en = graphene.String(required=True)
    phone_number = graphene.String()
    email = graphene.String()
    status = graphene.Boolean()
    parent = graphene.UUID()


class WorkforceOrganizationUnitDesignationInputType(OpenIMISMutation.Input):
    organization = graphene.UUID(required=True)
    unit = graphene.UUID(required=True)
    name_bn = graphene.String()
    name_en = graphene.String(required=True)
    status = graphene.Boolean()
    parent = graphene.UUID()
    designation_level = graphene.Int(required=True)
    designation_sequence = graphene.Int(required=True)


class WorkforceOrganizationEmployeeInputType(OpenIMISMutation.Input):
    designation = graphene.UUID(required=True)
    name_bn = graphene.String(required=True)
    name_en = graphene.String(required=True)
    gender = graphene.String()
    location = graphene.Int(required=True)
    address = graphene.String()
    phone_number = graphene.String()
    email = graphene.String()
    birth_date = graphene.String(required=True)
    nid = graphene.String()
    birth_certificate_no = graphene.String()
    passport_no = graphene.String()
    status = graphene.Boolean()
    related_user = graphene.UUID(required=True)


class WorkforceEmployerInputType(OpenIMISMutation.Input):
    employer_id = graphene.String(required=True, unique=True)
    employer_id_lima = graphene.String()
    name_bn = graphene.String()
    name_en = graphene.String(required=True)
    location = graphene.Int(required=True)
    address = graphene.String()
    phone_number = graphene.String()
    email = graphene.String()
    website = graphene.String()
    licence_type = graphene.String(required=True)
    licence_number = graphene.String()
    business_sector = graphene.String(required=True)
    foundation_date = graphene.String()
    association_name = graphene.String()
    association_membership_number = graphene.String()
    establishment_Name = graphene.String()
    establishment_date = graphene.String()
    status = graphene.Boolean()
    workforce_representative = graphene.UUID(required=True)
