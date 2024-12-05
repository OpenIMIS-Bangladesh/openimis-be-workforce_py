from django.db import models
from core.models import HistoryModel
from location.models import Location


class WorkforceRepresentative(HistoryModel):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=255)
    name_bn = models.CharField(max_length=255, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    location_id = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False,
        db_column="location_id"
    )
    address = models.TextField(null=True)
    phone_number = models.CharField(max_length=20, null=True)
    email = models.EmailField(max_length=255, null=True)
    nid = models.CharField(max_length=30, null=True)
    passport_no = models.CharField(max_length=30, null=True)
    birth_date = models.DateField(null=True)
    position = models.CharField(max_length=255, null=True)
    status = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'workforce_representative'


# Organizations responsible for managing
class WorkforceOrganization(HistoryModel):
    id = models.AutoField(primary_key=True)
    name_bn = models.CharField(max_length=255, null=True, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    location_id = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False,
        db_column="location_id"
    )
    address = models.TextField(null=True)
    phone_number = models.CharField(max_length=20, null=True)
    email = models.EmailField(max_length=255, null=True)
    website = models.URLField(max_length=200, null=True)
    status = models.BooleanField(default=1)
    parent_id = models.ForeignKey(
        "WorkforceOrganization",
        models.DO_NOTHING,
        db_column="parent_id",
        blank=True,
        null=True,
        related_name="children",
    )
    workforce_representative = models.ForeignKey(
        WorkforceRepresentative,
        models.DO_NOTHING,
        blank=False,
        null=False,
        db_column="workforce_representative_id"
    )

    class Meta:
        managed = True
        db_table = 'workforce_organizations'


class WorkforceOrganizationUnit(HistoryModel):
    id = models.AutoField(primary_key=True)
    organization_id = models.ForeignKey(
        WorkforceOrganization,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name='organization'
    )
    unit_level = models.SmallIntegerField(default=1)
    name_bn = models.CharField(max_length=255, null=True, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    phone_number = models.CharField(max_length=20, null=True)
    email = models.EmailField(max_length=255, null=True)
    status = models.BooleanField(default=1)
    parent_id = models.ForeignKey(
        "WorkforceOrganizationUnit",
        models.DO_NOTHING,
        db_column="parent_id",
        blank=True,
        null=True,
        related_name="children",
    )
    workforce_representative = models.ForeignKey(
        WorkforceRepresentative,
        models.DO_NOTHING,
        blank=False,
        null=False,
        db_column="workforce_representative_id"
    )

    class Meta:
        managed = True
        db_table = 'workforce_organization_units'


class WorkforceOrganizationUnitDesignation(HistoryModel):
    id = models.AutoField(primary_key=True)
    organization_id = models.ForeignKey(
        WorkforceOrganization,
        models.DO_NOTHING,
        blank=False,
        null=False,
    )
    unit_id = models.ForeignKey(
        WorkforceOrganizationUnit,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name='organization_unit'
    )
    name_bn = models.CharField(max_length=255, null=True, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    status = models.BooleanField(default=1)
    parent_id = models.ForeignKey(
        "WorkforceOrganizationUnitDesignation",
        models.DO_NOTHING,
        db_column="parent_id",
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
    id = models.AutoField(primary_key=True)
    designation_id = models.ForeignKey(
        WorkforceOrganizationUnitDesignation,
        models.DO_NOTHING,
        blank=False,
        null=False,
        db_column="designation_id"
    )
    name_bn = models.CharField(max_length=255, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    gender = models.CharField(max_length=30, null=True)
    location_id = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False,
        db_column="location_id"
    )
    address = models.TextField(null=True)
    phone_number = models.CharField(max_length=20, null=True)
    email = models.EmailField(max_length=255, null=True)
    birth_date = models.DateField(null=True)
    nid = models.CharField(max_length=30, null=True)
    birth_certificate_no = models.CharField(max_length=30, null=True)
    passport_no = models.CharField(max_length=30, null=True)
    status = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'workforce_organization_employee'


class WorkforceEmployer(HistoryModel):
    id = models.AutoField(primary_key=True)
    employer_id = models.CharField(max_length=255, unique=True)
    employer_id_lima = models.CharField(max_length=255, null=True)
    name_bn = models.CharField(max_length=255, null=True, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    location_id = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False,
        db_column="location_id"
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
        null=False,
        db_column="workforce_representative_id"
    )

    class Meta:
        managed = True
        db_table = 'workforce_employers'


class WorkforceOffice(HistoryModel):
    id = models.AutoField(primary_key=True)
    workforce_employer_id = models.ForeignKey(
        WorkforceEmployer,
        models.DO_NOTHING,
        blank=False,
        null=False,
        db_column="workforce_employer_id"
    )
    name_bn = models.CharField(max_length=255, null=True, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    location_id = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False,
        db_column="location_id"
    )
    address = models.TextField(null=True)
    phone_number = models.CharField(max_length=20, null=True)
    email = models.EmailField(max_length=255, null=True)
    website = models.URLField(max_length=200, null=True)
    parent_id = models.ForeignKey(
        "WorkforceOffice",
        models.DO_NOTHING,
        db_column="parent_id",
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
        db_column="workforce_representative_id"
    )

    class Meta:
        managed = True
        db_table = 'workforce_employer_offices'


class WorkforceFactory(HistoryModel):
    id = models.AutoField(primary_key=True)
    workforce_employer_id = models.ForeignKey(
        WorkforceEmployer,
        models.DO_NOTHING,
        blank=False,
        null=False,
        db_column="workforce_employer_id"
    )
    employer_id = models.CharField(max_length=255, null=True)
    employer_id_lima = models.CharField(max_length=255, null=True)
    name_bn = models.CharField(max_length=255, null=False, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    location_id = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False,
        db_column="location_id"
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
        db_column="workforce_representative_id"
    )

    class Meta:
        managed = True
        db_table = 'employer_factories'


class WorkforceEmployee(HistoryModel):
    id = models.AutoField(primary_key=True)
    employer_id = models.IntegerField()
    global_id = models.CharField(max_length=50, null=True)
    present_location_id = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="employee_present_location",
        db_column="present_location_id"
    )
    permanent_location_id = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="employee_permanent_location",
        db_column="permanent_location_id"
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

    class Meta:
        managed = True
        db_table = 'workforce_employee'
