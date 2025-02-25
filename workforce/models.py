from django.db import models
from core.models import HistoryModel, InteractiveUser
from location.models import Location


class WorkforceRepresentative(HistoryModel):
    type = models.CharField(max_length=255)
    name_bn = models.CharField(max_length=255, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False
    )
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    nid = models.CharField(max_length=30, null=True, blank=True)
    passport_no = models.CharField(max_length=30, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    position = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)
    related_user = models.ForeignKey(
        InteractiveUser,
        models.DO_NOTHING,
        blank=False,
        null=False
    )

    class Meta:
        managed = True
        db_table = 'workforce_representative'


# Organizations responsible for managing
class WorkforceOrganization(HistoryModel):
    type = models.CharField(max_length=255, null=True, blank=True)
    name_bn = models.CharField(max_length=255, null=True, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False
    )
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)
    parent = models.ForeignKey(
        "WorkforceOrganization",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="children",
    )
    workforce_representative = models.ForeignKey(
        WorkforceRepresentative,
        models.DO_NOTHING,
        blank=False,
        null=False,
    )

    class Meta:
        managed = True
        db_table = 'workforce_organizations'


class WorkforceOrganizationUnit(HistoryModel):
    organization = models.ForeignKey(
        WorkforceOrganization,
        models.DO_NOTHING,
        blank=False,
        null=False,
    )
    unit_level = models.SmallIntegerField(default=1)
    name_bn = models.CharField(max_length=255, null=True, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)
    parent = models.ForeignKey(
        "WorkforceOrganizationUnit",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="children",
    )

    class Meta:
        managed = True
        db_table = 'workforce_organization_units'


class WorkforceOrganizationUnitDesignation(HistoryModel):
    organization = models.ForeignKey(
        WorkforceOrganization,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name='organization'
    )
    unit = models.ForeignKey(
        WorkforceOrganizationUnit,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name='unit_designations'
    )
    name_bn = models.CharField(max_length=255, null=True, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    status = models.CharField(max_length=30, null=True, blank=True)
    parent = models.ForeignKey(
        "WorkforceOrganizationUnitDesignation",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="children",
    )
    designation_level = models.SmallIntegerField(default=True)
    designation_sequence = models.SmallIntegerField(default=True)

    class Meta:
        managed = True
        db_table = 'workforce_organization_unit_designations'


class WorkforceOrganizationEmployee(HistoryModel):
    name_bn = models.CharField(max_length=255, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    gender = models.CharField(max_length=30, null=True, blank=True)
    location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False
    )
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    nid = models.CharField(max_length=30, null=True, blank=True)
    birth_certificate_no = models.CharField(max_length=30, null=True, blank=True)
    passport_no = models.CharField(max_length=30, null=True, blank=True)
    first_joining_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)
    related_user = models.ForeignKey(
        InteractiveUser,
        models.DO_NOTHING,
        blank=False,
        null=False
    )

    class Meta:
        managed = True
        db_table = 'workforce_organization_employee'


class WorkforceOrganizationEmployeeDesignation(HistoryModel):
    designation = models.ForeignKey(
        WorkforceOrganizationUnitDesignation,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="employee_designations"
    )
    employee = models.ForeignKey(
        "WorkforceOrganizationEmployee",
        models.DO_NOTHING,
        related_name='designations',
        blank=False,
        null=False
    )
    incharge_label = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_organization_employee_designations'


class WorkforceEmployer(HistoryModel):
    employer_id = models.CharField(max_length=255, unique=True)
    employer_id_lima = models.CharField(max_length=255, null=True, blank=True)
    name_bn = models.CharField(max_length=255, null=True, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False
    )
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=200, null=True, blank=True)
    licence_type = models.CharField(max_length=255)
    licence_number = models.CharField(max_length=255, null=True, blank=True)
    business_sector = models.CharField(max_length=255)
    foundation_date = models.DateField(null=True, blank=True)
    association_name = models.CharField(null=True, blank=True)
    association_membership_number = models.CharField(null=True, blank=True)
    establishment_Name = models.CharField(null=True, blank=True)
    establishment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)
    workforce_representative = models.ForeignKey(
        WorkforceRepresentative,
        models.DO_NOTHING,
        blank=False,
        null=False
    )

    class Meta:
        managed = True
        db_table = 'workforce_employers'


class WorkforceOffice(HistoryModel):
    workforce_employer = models.ForeignKey(
        WorkforceEmployer,
        models.DO_NOTHING,
        blank=False,
        null=False
    )
    name_bn = models.CharField(max_length=255, null=True, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False
    )
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=200, null=True, blank=True)
    parent = models.ForeignKey(
        "WorkforceOffice",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="children",
    )
    status = models.CharField(max_length=30, null=True, blank=True)
    is_same_company_representative = models.SmallIntegerField(default=0)
    workforce_representative = models.ForeignKey(
        WorkforceRepresentative,
        models.DO_NOTHING,
        blank=False,
        null=False,
    )

    class Meta:
        managed = True
        db_table = 'workforce_employer_offices'


class WorkforceFactory(HistoryModel):
    workforce_employer = models.ForeignKey(
        WorkforceEmployer,
        models.DO_NOTHING,
        blank=False,
        null=False,
    )
    employer_id = models.CharField(max_length=255, null=True, blank=True)
    employer_id_lima = models.CharField(max_length=255, null=True, blank=True)
    name_bn = models.CharField(max_length=255, null=False, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False
    )
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)
    is_same_company_representative = models.SmallIntegerField(default=0)
    workforce_representative = models.ForeignKey(
        WorkforceRepresentative,
        models.DO_NOTHING,
        blank=False,
        null=False,
    )

    class Meta:
        managed = True
        db_table = 'workforce_employer_factories'


class WorkforceEmployee(HistoryModel):
    employee_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    employee_id_lima = models.CharField(max_length=255, null=True, blank=True)
    insurance_number = models.CharField(max_length=50, unique=True)
    employee_type = models.CharField(max_length=16, null=True, blank=True, db_comment="office/factory employee")
    global_id = models.CharField(max_length=50, null=True, blank=True)
    present_location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="employee_present_location",
    )
    permanent_location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="employee_permanent_location",
    )
    first_name_bn = models.CharField(max_length=255, null=True, blank=True,
                                     db_comment='Translatable first name field. May use any language')
    last_name_bn = models.CharField(max_length=255, null=True, blank=True,
                                    db_comment='Translatable last name field. May use any language')
    other_name = models.CharField(max_length=255, null=True, blank=True, db_comment='Other name field')
    first_name_en = models.CharField(max_length=255, null=True, blank=True)
    last_name_en = models.CharField(max_length=255, null=True, blank=True)
    father_name_bn = models.CharField(max_length=255, null=True, blank=True)
    father_name_en = models.CharField(max_length=255, null=True, blank=True)
    mother_name_bn = models.CharField(max_length=255, null=True, blank=True)
    mother_name_en = models.CharField(max_length=255, null=True, blank=True)
    spouse_name_bn = models.CharField(max_length=255, null=True, blank=True)
    spouse_name_en = models.CharField(max_length=255, null=True, blank=True)
    citizenship = models.CharField(max_length=50, default='Bangladeshi')
    privacy_law = models.CharField(max_length=255, null=True, blank=True)
    marital_status = models.CharField(max_length=30, null=True, blank=True)
    gender = models.CharField(max_length=30, null=True, blank=True)
    photo_path = models.CharField(max_length=255, null=True, blank=True)
    photo_date = models.DateField(null=True, blank=True)
    position = models.CharField(max_length=255, null=True, blank=True)
    monthly_earning = models.CharField(max_length=255, null=True, blank=True)
    reference_salary = models.CharField(max_length=255, null=True, blank=True)
    present_address = models.TextField(null=True, blank=True)
    permanent_address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    nid = models.CharField(max_length=30, null=True, blank=True)
    birth_certificate_no = models.CharField(max_length=30, null=True, blank=True)
    passport_no = models.CharField(max_length=30, null=True, blank=True)
    registration_date = models.DateField(null=True, blank=True)
    life_status = models.CharField(max_length=30, null=True, blank=True)
    disability_status = models.CharField(max_length=30, null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)
    related_user = models.ForeignKey(
        InteractiveUser,
        models.DO_NOTHING,
        blank=False,
        null=False
    )

    class Meta:
        managed = True
        db_table = 'workforce_employee'


class WorkforceEmployeeDesignation(HistoryModel):
    company_id = models.CharField(max_length=30)
    factory_id = models.CharField(null=True, blank=True, max_length=30)
    office_id = models.CharField(null=True, blank=True, max_length=30)
    join_date = models.DateField(null=True, blank=True)
    resignation_date = models.DateField(null=True, blank=True)
    resignation_reason = models.TextField(null=True, blank=True)
    monthly_salary = models.CharField(null=True, blank=True, max_length=30)
    status = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_employee_designation'


class WorkforceDocument(HistoryModel):
    holder = models.CharField()
    holder_type = models.CharField(max_length=30, null=True, blank=True)
    verifier = models.ForeignKey(
        InteractiveUser,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="verifier"  # Unique related name
    )
    approver = models.ForeignKey(
        InteractiveUser,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="approver"  # Unique related name
    )
    document_type = models.CharField(max_length=30, null=False, blank=False)
    path = models.CharField(max_length=255, null=True, blank=True)
    submission_date = models.DateField(null=True, blank=True)
    verification_date = models.DateField(null=True, blank=True)
    approval_date = models.DateField(null=True, blank=True)
    remarks = models.CharField(max_length=512, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_documents'


class Bank(HistoryModel):
    name_bn = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255, null=True, blank=True)
    parent = models.ForeignKey(
        "Bank",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="children",
    )
    headquarter_address = models.CharField(max_length=255, null=True, blank=True)
    location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=True,
        null=True
    )
    routing_number = models.CharField(max_length=50, null=True, blank=True)
    contact_number = models.CharField(max_length=30, null=True, blank=True)
    type = models.CharField(max_length=30, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_banks'


class WorkforceEmployeeDependent(HistoryModel):
    eis_insurance_no = models.CharField(max_length=50, null=True, blank=True)
    first_name_bn = models.CharField(max_length=255, null=True, blank=True)
    last_name_bn = models.CharField(max_length=255, null=True, blank=True)
    first_name_en = models.CharField(max_length=255)
    last_name_en = models.CharField(max_length=255, null=True, blank=True)
    father_name_bn = models.CharField(max_length=255, null=True, blank=True)
    father_name_en = models.CharField(max_length=255, null=True, blank=True)
    mother_name_bn = models.CharField(max_length=255, null=True, blank=True)
    mother_name_en = models.CharField(max_length=255, null=True, blank=True)
    marital_status = models.CharField(max_length=30)
    gender = models.CharField(max_length=30)
    occupation = models.CharField(max_length=30)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    birth_date = models.DateField()
    nid = models.CharField(max_length=30, null=True, blank=True)
    birth_certificate_no = models.CharField(max_length=30, null=True, blank=True)
    present_location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="employee_dependent_present_location",
    )
    permanent_location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="employee_dependent_permanent_location",
    )
    life_status = models.CharField(max_length=30)
    death_date = models.DateField(null=True, blank=True)
    disability_status = models.CharField(max_length=30, null=True, blank=True)
    relation_type = models.CharField(max_length=50)
    relation_with_worker = models.CharField(max_length=50)
    last_verification_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_employee_dependent'


class WorkforceEmployeeAccident(HistoryModel):
    employee = models.ForeignKey(
        WorkforceEmployee,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="employee"  # Unique related name
    )
    injury_type = models.CharField(max_length=30, default="deceased")
    accident_date = models.DateField()
    accident_time = models.CharField()
    accident_type = models.CharField(max_length=30)
    duty_status = models.CharField(max_length=30)
    in_outside_factory = models.CharField(max_length=30)
    death_date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    accident_location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="employee_accident_location",
    )
    status = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_employee_accident'
