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
        related_name='organization_unit'
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
        null=False
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
    workforce_employer = models.ForeignKey(
        WorkforceEmployer,
        models.DO_NOTHING,
        blank=False,
        null=False,
    )
    workforce_office = models.ForeignKey(
        WorkforceOffice,
        models.DO_NOTHING,
        blank=True,
        null=True,
    )
    workforce_factory = models.ForeignKey(
        WorkforceFactory,
        models.DO_NOTHING,
        blank=True,
        null=True,
    )
    employee_id = models.CharField(max_length=255, null=True, blank=True)
    employee_id_lima = models.CharField(max_length=255, null=True, blank=True)
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
    name_bn = models.CharField(max_length=255, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    fathers_name = models.CharField(max_length=255, null=True, blank=True)
    mothers_name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=30, null=True, blank=True)
    marital_status = models.CharField(max_length=30, null=True, blank=True)
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
