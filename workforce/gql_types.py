import graphene

from core.schema import OpenIMISMutation


class WorkforceRepresentativeInputType(OpenIMISMutation.Input):
    id = graphene.String(required=False)
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
    id = graphene.String(required=False)
    name_bn = graphene.String()
    name_en = graphene.String(required=True)
    location = graphene.String(required=True)
    address = graphene.String()
    phone_number = graphene.String()
    email = graphene.String()
    website = graphene.String()
    status = graphene.Boolean()
    parent_id = graphene.Int()
    workforce_representative_id = graphene.UUID(required=True)


class WorkforceOrganizationUnitInputType(OpenIMISMutation.Input):
    id = graphene.String(required=False)
    organization = graphene.UUID(required=True)
    unit_level = graphene.String()
    name_bn = graphene.String()
    name_en = graphene.String(required=True)
    phone_number = graphene.String()
    email = graphene.String()
    status = graphene.Boolean()
    parent = graphene.UUID()


class WorkforceOrganizationUnitDesignationInputType(OpenIMISMutation.Input):
    id = graphene.String(required=False)
    organization = graphene.UUID(required=True)
    unit = graphene.UUID(required=True)
    name_bn = graphene.String()
    name_en = graphene.String(required=True)
    status = graphene.Boolean()
    parent = graphene.UUID()
    designation_level = graphene.Int(required=True)
    designation_sequence = graphene.Int(required=True)


class WorkforceOrganizationEmployeeInputType(OpenIMISMutation.Input):
    id = graphene.String(required=False)
    name_bn = graphene.String(required=True)
    name_en = graphene.String(required=True)
    gender = graphene.String()
    location_id = graphene.String(required=True)
    address = graphene.String()
    phone_number = graphene.String()
    email = graphene.String()
    birth_date = graphene.String()
    nid = graphene.String()
    birth_certificate_no = graphene.String()
    passport_no = graphene.String()
    first_joining_date = graphene.String()
    status = graphene.Boolean()
    related_user_id = graphene.UUID(required=False)


class WorkforceOrganizationEmployeeDesignationInputType(OpenIMISMutation.Input):
    designation_id = graphene.UUID(required=True)
    employee_id = graphene.UUID(required=True)
    incharge_label = graphene.String(required=False)
    status = graphene.Boolean(required=False)
    joining_date = graphene.String(required=False)
    release_date = graphene.String(required=False)
    released_by_id = graphene.UUID(required=False)


class WorkforceEmployerInputType(OpenIMISMutation.Input):
    id = graphene.String(required=False)
    employer_id = graphene.String(required=True, unique=True)
    employer_id_lima = graphene.String()
    name_bn = graphene.String()
    name_en = graphene.String(required=True)
    location = graphene.String(required=True)
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


class WorkforceOfficeInputType(OpenIMISMutation.Input):
    id = graphene.String(required=False)
    workforce_employer = graphene.UUID(required=True)
    name_bn = graphene.String()
    name_en = graphene.String(required=True)
    location = graphene.String(required=True)
    address = graphene.String()
    phone_number = graphene.String()
    email = graphene.String()
    website = graphene.String()
    parent = graphene.UUID()
    status = graphene.Boolean()
    workforce_representative = graphene.UUID(required=True)


class WorkforceFactoryInputType(OpenIMISMutation.Input):
    id = graphene.String(required=False)
    workforce_employer = graphene.UUID(required=True)
    employer_id = graphene.String()
    employer_id_lima = graphene.String()
    name_bn = graphene.String()
    name_en = graphene.String(required=True)
    location = graphene.String(required=True)
    address = graphene.String()
    phone_number = graphene.String()
    email = graphene.String()
    website = graphene.String()
    status = graphene.Boolean()
    workforce_representative = graphene.UUID(required=True)


class WorkforceEmployeeInputType(OpenIMISMutation.Input):
    id = graphene.String(required=False)
    employer_id = graphene.UUID(required=True)
    global_id = graphene.String()
    present_location = graphene.String(required=True)
    permanent_location = graphene.String(required=True)
    name_bn = graphene.String(required=True)
    name_en = graphene.String(required=True)
    fathers_name = graphene.String()
    mothers_name = graphene.String()
    gender = graphene.String()
    marital_status = graphene.String()
    photo_path = graphene.String()
    photo_date = graphene.String()
    position = graphene.String()
    monthly_earning = graphene.String()
    reference_salary = graphene.String()
    present_address = graphene.String()
    permanent_address = graphene.String()
    phone_number = graphene.String()
    email = graphene.String()
    birth_date = graphene.String()
    nid = graphene.String()
    birth_certificate_no = graphene.String()
    passport_no = graphene.String()
    status = graphene.Boolean()
    related_user = graphene.UUID(required=True)
