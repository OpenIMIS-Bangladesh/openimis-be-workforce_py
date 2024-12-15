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
    address = models.TextField(null=True)
    phone_number = models.CharField(max_length=20, null=True)
    email = models.EmailField(max_length=255, null=True)
    nid = models.CharField(max_length=30, null=True)
    passport_no = models.CharField(max_length=30, null=True)
    birth_date = models.DateField(null=True)
    position = models.CharField(max_length=255, null=True)
    status = models.BooleanField(default=True)
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
    address = models.TextField(null=True)
    phone_number = models.CharField(max_length=20, null=True)
    email = models.EmailField(max_length=255, null=True)
    website = models.URLField(max_length=200, null=True)
    status = models.BooleanField(default=1)
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
    phone_number = models.CharField(max_length=20, null=True)
    email = models.EmailField(max_length=255, null=True)
    status = models.BooleanField(default=1)
    parent = models.ForeignKey(
        "WorkforceOrganizationUnit",
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
    status = models.BooleanField(default=1)
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
    designation = models.ForeignKey(
        WorkforceOrganizationUnitDesignation,
        models.DO_NOTHING,
        blank=False,
        null=False
    )
    name_bn = models.CharField(max_length=255, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    gender = models.CharField(max_length=30, null=True)
    location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False
    )
    address = models.TextField(null=True)
    phone_number = models.CharField(max_length=20, null=True)
    email = models.EmailField(max_length=255, null=True)
    birth_date = models.DateField(null=True)
    nid = models.CharField(max_length=30, null=True)
    birth_certificate_no = models.CharField(max_length=30, null=True)
    passport_no = models.CharField(max_length=30, null=True)
    status = models.BooleanField(default=True)
    related_user = models.ForeignKey(
        InteractiveUser,
        models.DO_NOTHING,
        blank=False,
        null=False
    )

    class Meta:
        managed = True
        db_table = 'workforce_organization_employee'


class WorkforceEmployer(HistoryModel):
    employer_id = models.CharField(max_length=255, unique=True)
    employer_id_lima = models.CharField(max_length=255, null=True)
    name_bn = models.CharField(max_length=255, null=True, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False
    )
    address = models.TextField(null=True)
    phone_number = models.CharField(max_length=20, null=True)
    email = models.EmailField(max_length=255, null=True)
    website = models.URLField(max_length=200, null=True)
    licence_type = models.CharField(max_length=255)
    licence_number = models.CharField(max_length=255, null=True)
    business_sector = models.CharField(max_length=255)
    foundation_date = models.DateField(null=True)
    association_name = models.CharField(null=True)
    association_membership_number = models.CharField(null=True)
    establishment_Name = models.CharField(null=True)
    establishment_date = models.DateField(null=True)
    status = models.BooleanField(default=True)
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
    address = models.TextField(null=True)
    phone_number = models.CharField(max_length=20, null=True)
    email = models.EmailField(max_length=255, null=True)
    website = models.URLField(max_length=200, null=True)
    parent = models.ForeignKey(
        "WorkforceOffice",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="children",
    )
    status = models.BooleanField(default=True)
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
    employer_id = models.CharField(max_length=255, null=True)
    employer_id_lima = models.CharField(max_length=255, null=True)
    name_bn = models.CharField(max_length=255, null=False, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False
    )
    address = models.TextField(null=True)
    phone_number = models.CharField(max_length=20, null=True)
    email = models.EmailField(max_length=255, null=True)
    website = models.URLField(max_length=200, null=True)
    status = models.BooleanField(default=True)
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
    employer_id = models.IntegerField()
    global_id = models.CharField(max_length=50, null=True)
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
    fathers_name = models.CharField(max_length=255, null=True)
    mothers_name = models.CharField(max_length=255, null=True)
    gender = models.CharField(max_length=30, null=True)
    marital_status = models.CharField(max_length=30, null=True)
    photo_path = models.CharField(max_length=255, null=True)
    photo_date = models.DateField(null=True)
    position = models.CharField(max_length=255, null=True)
    monthly_earning = models.CharField(max_length=255, null=True)
    reference_salary = models.CharField(max_length=255, null=True)
    present_address = models.TextField(null=True)
    permanent_address = models.TextField(null=True)
    phone_number = models.CharField(max_length=20, null=True)
    email = models.EmailField(max_length=255, null=True)
    birth_date = models.DateField(null=True)
    nid = models.CharField(max_length=30, null=True)
    birth_certificate_no = models.CharField(max_length=30, null=True)
    passport_no = models.CharField(max_length=30, null=True)
    status = models.BooleanField(default=True)
    related_user = models.ForeignKey(
        InteractiveUser,
        models.DO_NOTHING,
        blank=False,
        null=False
    )

    class Meta:
        managed = True
        db_table = 'workforce_employee'
