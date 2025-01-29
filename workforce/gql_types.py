import graphene

from core.schema import OpenIMISMutation


class WorkforceRepresentativeInputType(OpenIMISMutation.Input):
    id = graphene.String(required=False)
    type = graphene.String(requred=True)
    name_bn = graphene.String(required=True)
    name_en = graphene.String(required=True)
    location_id = graphene.String(required=True)
    address = graphene.String(required=True)
    phone_number = graphene.String()
    email = graphene.String()
    nid = graphene.String()
    passport_no = graphene.String()
    birth_date = graphene.String(required=True)
    position = graphene.String(required=True)
    status = graphene.String()
    related_user_id = graphene.String()


class WorkforceOrganizationInputType(OpenIMISMutation.Input):
    id = graphene.String(required=False)
    name_bn = graphene.String()
    name_en = graphene.String(required=True)
    location_id = graphene.String(required=True)
    address = graphene.String()
    phone_number = graphene.String()
    email = graphene.String(required=True)
    website = graphene.String()
    status = graphene.String()
    parent_id = graphene.Int()
    workforce_representative_id = graphene.UUID(required=True)


class WorkforceOrganizationUnitInputType(OpenIMISMutation.Input):
    id = graphene.String(required=False)
    organization_id = graphene.UUID(required=True)
    unit_level = graphene.String()
    name_bn = graphene.String()
    name_en = graphene.String(required=True)
    phone_number = graphene.String()
    email = graphene.String()
    status = graphene.String()
    parent_id = graphene.UUID()


class WorkforceOrganizationUnitDesignationInputType(OpenIMISMutation.Input):
    id = graphene.String(required=False)
    organization_id = graphene.UUID(required=True)
    unit_id = graphene.UUID(required=True)
    name_bn = graphene.String()
    name_en = graphene.String(required=True)
    status = graphene.String()
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
    status = graphene.String()
    related_user_id = graphene.UUID(required=False)


class WorkforceOrganizationEmployeeDesignationInputType(OpenIMISMutation.Input):
    id = graphene.UUID(required=False)
    designation_id = graphene.UUID(required=True)
    employee_id = graphene.UUID(required=True)
    incharge_label = graphene.String(required=False)
    status = graphene.String(required=False)
    joining_date = graphene.String(required=False)
    release_date = graphene.String(required=False)


class WorkforceEmployerInputType(OpenIMISMutation.Input):
    id = graphene.String(required=False)
    employer_id = graphene.String(required=True, unique=True)
    employer_id_lima = graphene.String()
    name_bn = graphene.String()
    name_en = graphene.String(required=True)
    location_id = graphene.String(required=True)
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
    status = graphene.String()
    workforce_representative_id = graphene.UUID(required=True)


class WorkforceEmployerStatusInput(OpenIMISMutation.Input):
    id = graphene.String(required=True)
    status = graphene.String(required=True)


class WorkforceOfficeInputType(OpenIMISMutation.Input):
    id = graphene.String(required=False)
    workforce_employer_id = graphene.UUID(required=True)
    name_bn = graphene.String()
    name_en = graphene.String(required=True)
    location_id = graphene.String(required=True)
    address = graphene.String()
    phone_number = graphene.String()
    email = graphene.String()
    website = graphene.String()
    parent_id = graphene.UUID()
    status = graphene.String()
    is_same_company_representative = graphene.String()
    workforce_representative_id = graphene.UUID(required=True)


class WorkforceFactoryInputType(OpenIMISMutation.Input):
    id = graphene.String(required=False)
    workforce_employer_id = graphene.UUID(required=True)
    employer_id = graphene.String()
    employer_id_lima = graphene.String()
    name_bn = graphene.String()
    name_en = graphene.String(required=True)
    location_id = graphene.String(required=True)
    address = graphene.String()
    phone_number = graphene.String()
    email = graphene.String()
    website = graphene.String()
    status = graphene.String()
    is_same_company_representative = graphene.String()
    workforce_representative_id = graphene.UUID()


class WorkforceEmployeeInputType(OpenIMISMutation.Input):
    id = graphene.String(required=False)
    workforce_employer_id = graphene.UUID(required=True)
    workforce_office = graphene.UUID(required=False)
    workforce_factory = graphene.UUID(required=False)
    employee_id = graphene.String(required=False)
    employee_id_lima = graphene.String(required=False)
    employee_type = graphene.String(required=True)
    global_id = graphene.String()
    present_location_id = graphene.String(required=True)
    permanent_location_id = graphene.String(required=True)
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
    nid = graphene.String(required=True)
    birth_certificate_no = graphene.String()
    passport_no = graphene.String()
    status = graphene.String()
    related_user_id = graphene.UUID(required=False)


class WorkforceDocumentInputType(OpenIMISMutation.Input):
    id = graphene.String(required=False)
    holder = graphene.UUID()
    holder_type = graphene.String(required=True)
    verifier_id = graphene.UUID()
    approver_id = graphene.UUID()
    document_type = graphene.String()
    path = graphene.String()
    submission_date = graphene.String()
    verification_date = graphene.String()
    approval_date = graphene.String()
    remarks = graphene.String()
    status = graphene.String()