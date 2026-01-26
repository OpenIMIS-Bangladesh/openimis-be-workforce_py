from django.db import models
from core.models import HistoryModel, InteractiveUser
from core.models.user import Role
from location.models import Location
from django.utils import timezone
from datetime import timedelta
import secrets
import uuid
from datetime import datetime as py_datetime


def generate_otp():
    return str(secrets.randbelow(90000) + 10000)


def expiry_time():
    return timezone.now() + timedelta(minutes=5)


class WorkforceRepresentative(HistoryModel):
    type = models.CharField(max_length=255)
    name_bn = models.CharField(
        max_length=255, db_comment='Translatable name field. May use any language')
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
    name_bn = models.CharField(
        max_length=255, null=True, db_comment='Translatable name field. May use any language')
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
    name_bn = models.CharField(
        max_length=255, null=True, db_comment='Translatable name field. May use any language')
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
    name_bn = models.CharField(
        max_length=255, null=True, db_comment='Translatable name field. May use any language')
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
    name_bn = models.CharField(
        max_length=255, db_comment='Translatable name field. May use any language', null=True, blank=True)
    name_en = models.CharField(max_length=255, db_comment='English name field', null=True, blank=True)
    gender = models.CharField(max_length=30, null=True, blank=True)
    location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=True,
        null=True
    )
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    nid = models.CharField(max_length=30, null=True, blank=True)
    birth_certificate_no = models.CharField(
        max_length=30, null=True, blank=True)
    passport_no = models.CharField(max_length=30, null=True, blank=True)
    first_joining_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)
    related_user = models.ForeignKey(
        InteractiveUser,
        models.DO_NOTHING,
        blank=False,
        null=False
    )
    association = models.ForeignKey(
        "WorkforceAssociation",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="organization_employee_association"
    )
    all_association = models.ForeignKey(
        "WorkforceAllAssociation",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="all_organization_employee_association"
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
    name_bn = models.CharField(
        max_length=255, null=True, db_comment='Translatable name field. May use any language')
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
    name_bn = models.CharField(
        max_length=255, null=True, db_comment='Translatable name field. May use any language')
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
        blank=True,
        null=True,
    )
    employer_id = models.CharField(max_length=255, null=True, blank=True)
    employer_id_lima = models.CharField(max_length=255, null=True, blank=True)
    name_bn = models.TextField(null=False, db_comment='Translatable name field. May use any language')
    name_en = models.TextField(db_comment='English name field')
    group_name = models.TextField(null=True, blank=True)
    license_type = models.CharField(max_length=200, null=True, blank=True)
    location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="location",
    )

    office_location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="office_location",
    )
    future_date = models.DateField(null=True, blank=True)
    date_of_eis_incorporation = models.DateField(null=True, blank=True)
    date_of_factory_establishment = models.DateField(null=True, blank=True)
    membership_no = models.CharField(max_length=200, null=True, blank=True)
    business_sector = models.TextField(null=True, blank=True)
    license_no = models.CharField(max_length=200, null=True, blank=True)
    lima_registration_number = models.CharField(max_length=200, null=True, blank=True)
    approximate_number_of_employee = models.CharField(max_length=200, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    office_address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)
    is_same_company_representative = models.SmallIntegerField(default=0)
    association_type = models.CharField(max_length=50, null=True, blank=True)
    minimum_salary = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    registration_date = models.DateField(null=True, blank=True)
    registration_expiry_date= models.DateField(null=True, blank=True)
    workforce_representative = models.ForeignKey(
        WorkforceRepresentative,
        models.DO_NOTHING,
        blank=True,
        null=True,
    )
    all_association = models.ForeignKey(
        "WorkforceAllAssociation",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="factory_all_association"
    )

    class Meta:
        managed = True
        db_table = 'workforce_employer_factories'


class WorkforceEmployee(HistoryModel):
    employee_id = models.CharField(
        max_length=255, null=True, blank=True, unique=True)
    employee_id_lima = models.CharField(max_length=255, null=True, blank=True)
    workforce_factory = models.ForeignKey(
        WorkforceFactory,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_employee_factory",
    )
    insurance_number = models.CharField(max_length=50, null=True, blank=True)
    employee_type = models.CharField(
        max_length=16, null=True, blank=True, db_comment="office/factory employee")
    global_id = models.CharField(max_length=50, null=True, blank=True)
    present_location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="employee_present_location",
    )
    permanent_location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="employee_permanent_location",
    )
    first_name_bn = models.CharField(max_length=255, null=True, blank=True,
                                     db_comment='Translatable first name field. May use any language')
    last_name_bn = models.CharField(max_length=255, null=True, blank=True,
                                    db_comment='Translatable last name field. May use any language')
    other_name = models.CharField(
        max_length=255, null=True, blank=True, db_comment='Other name field')
    first_name_en = models.CharField(max_length=255, null=True, blank=True)
    last_name_en = models.CharField(max_length=255, null=True, blank=True)
    father_name_bn = models.CharField(max_length=255, null=True, blank=True)
    father_name_en = models.CharField(max_length=255, null=True, blank=True)
    mother_name_bn = models.CharField(max_length=255, null=True, blank=True)
    mother_name_en = models.CharField(max_length=255, null=True, blank=True)
    spouse_name_bn = models.CharField(max_length=255, null=True, blank=True)
    spouse_name_en = models.CharField(max_length=255, null=True, blank=True)
    citizenship = models.CharField(max_length=50, default='BD')
    privacy_law = models.CharField(max_length=255, null=True, blank=True)
    marital_status = models.CharField(max_length=512, null=True, blank=True)
    gender = models.CharField(max_length=30, null=True, blank=True)
    photo_path = models.CharField(max_length=255, null=True, blank=True)
    photo_date = models.DateField(null=True, blank=True)
    position = models.CharField(max_length=255, null=True, blank=True)
    monthly_earning = models.CharField(max_length=255, null=True, blank=True)
    reference_salary = models.CharField(max_length=255, null=True, blank=True)
    present_address = models.TextField(null=True, blank=True)
    permanent_address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(
        max_length=20, null=True, blank=True, unique=True)
    email = models.CharField(max_length=255, null=True,
                             blank=True, unique=True)
    birth_date = models.DateField(null=True, blank=True)
    nid = models.CharField(max_length=30, null=True, blank=True, unique=True)
    birth_certificate_no = models.CharField(
        max_length=30, null=True, blank=True, unique=True)
    passport_no = models.CharField(
        max_length=30, null=True, blank=True, unique=True)
    registration_date = models.DateField(null=True, blank=True)
    life_status = models.CharField(max_length=30, null=True, blank=True)
    disability_status = models.CharField(max_length=30, null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)
    related_user = models.ForeignKey(
        InteractiveUser,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="employee_related_user",
    )

    class Meta:
        managed = True
        db_table = 'workforce_employee'


class WorkforceEmployeeDesignation(HistoryModel):
    workforce_application = models.ForeignKey(
        "WorkforceApplication",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="employee_designation_application",
    )
    workforce_employee = models.ForeignKey(
        WorkforceEmployee,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="employee_designation_employee_id",
    )
    workforce_company = models.ForeignKey(
        WorkforceEmployer,
        models.DO_NOTHING,
        blank=False,
        null=False,
    )
    workforce_factory = models.ForeignKey(
        WorkforceFactory,
        models.DO_NOTHING,
        blank=True,
        null=True,
    )
    workforce_office = models.ForeignKey(
        WorkforceOffice,
        models.DO_NOTHING,
        blank=True,
        null=True,
    )
    position = models.CharField(max_length=255, null=True, blank=True)
    join_date = models.DateField(null=True, blank=True)
    resignation_date = models.DateField(null=True, blank=True)
    resignation_reason = models.TextField(null=True, blank=True)
    monthly_salary = models.CharField(null=True, blank=True, max_length=30)
    status = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_employee_designation'


class WorkforceDocument(HistoryModel):
    workforce_application = models.ForeignKey(
        "WorkforceApplication",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_document_application",
    )
    holder = models.ForeignKey(
        InteractiveUser,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="document_owner"
    )
    holder_type = models.CharField(max_length=512, null=True, blank=True)
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
    factory = models.ForeignKey(
        WorkforceFactory,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="factory"  # Unique related name
    )
    workforce_document_type = models.ForeignKey(
        "WorkforceDocumentType",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="document_type_for_documents"  # Unique related name
    )
    workforce_dependent = models.ForeignKey(
        "WorkforceEmployeeDependent",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_dependent"  # Unique related name
    )
    application_summary = models.ForeignKey(
        "WorkforceApplicationSummary",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="document_application_summary"
    )
    workforce_employee_banking_info = models.ForeignKey(
        "WorkforceEmployeeBankingInfo",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="employee_banking_info_for_documents"
    )
    note = models.CharField(max_length=1024, null=True, blank=True)
    document_type = models.CharField(max_length=512, null=False, blank=False)
    path = models.CharField(max_length=512, null=True, blank=True)
    url = models.CharField(max_length=512, null=True, blank=True)
    submission_date = models.DateField(null=True, blank=True)
    verification_date = models.DateField(null=True, blank=True)
    approval_date = models.DateField(null=True, blank=True)
    remarks = models.CharField(max_length=512, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_documents'


class Bank(HistoryModel):
    name_bn = models.CharField(max_length=255, null=True, blank=True)
    name_en = models.CharField(max_length=255, null=True, blank=True)
    bank_code = models.CharField(max_length=15, null=True, blank=True)
    branch_code = models.CharField(max_length=15, null=True, blank=True)
    district_code = models.CharField(max_length=15, null=True, blank=True)
    district_name_en = models.CharField(max_length=255, null=True, blank=True)
    district_name_bn = models.CharField(max_length=255, null=True, blank=True)
    routing_number = models.CharField(max_length=15, null=True, blank=True)
    parent = models.ForeignKey(
        "Bank",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="children",
    )
    contact_number = models.CharField(max_length=30, null=True, blank=True)
    type = models.CharField(max_length=30, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_banks'


class WorkforceEmployeeDependent(HistoryModel):
    workforce_application = models.ForeignKey(
        "WorkforceApplication",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_employee_dependent_application",
    )
    eis_insurance_no = models.CharField(max_length=512, null=True, blank=True)
    name_bn = models.CharField(max_length=512, null=True, blank=True)
    name_en = models.CharField(max_length=512, null=True, blank=True)
    father_name_bn = models.CharField(max_length=512, null=True, blank=True)
    father_name_en = models.CharField(max_length=512, null=True, blank=True)
    mother_name_bn = models.CharField(max_length=512, null=True, blank=True)
    mother_name_en = models.CharField(max_length=512, null=True, blank=True)
    marital_status = models.CharField(max_length=512, null=True, blank=True)
    gender = models.CharField(max_length=512, null=True, blank=True)
    occupation = models.CharField(max_length=512, null=True, blank=True)
    email = models.CharField(max_length=512, null=True, blank=True)
    phone_number = models.CharField(null=True, blank=True, max_length=512)
    birth_date = models.DateField(null=True, blank=True)
    nid = models.CharField(max_length=512, null=True, blank=True)
    birth_certificate_no = models.CharField(
        max_length=512, null=True, blank=True)
    bank = models.ForeignKey(
        Bank,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_banks",
    )
    bank_account_no = models.CharField(max_length=50, null=True, blank=True)
    bank_account_holder_name = models.CharField(max_length=255, null=True, blank=True)
    eis_payment_type = models.CharField(max_length=50, null=True, blank=True)
    eis_calculated_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    eis_approved_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    eis_initial_monthly_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    eis_monthly_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    pv_factor = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    initial_replacement_rate = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    parent_dependent = models.ForeignKey(
        "WorkforceEmployeeDependent",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="children",
    )
    percentage_of_cf_grant = models.CharField(max_length=30, null=True, blank=True)
    present_location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="employee_dependent_present_location",
    )
    permanent_location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="employee_dependent_permanent_location",
    )
    present_address = models.JSONField(null=True, blank=True)
    permanent_address = models.JSONField(null=True, blank=True)
    life_status = models.CharField(max_length=512, null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    disability_status = models.CharField(max_length=512, null=True, blank=True)
    disability_type = models.TextField(null=True, blank=True)
    relation_with_worker = models.CharField(
        max_length=512, null=True, blank=True)
    last_verification_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)
    is_eligible = models.BooleanField(default=False)
    account_holder_type = models.CharField(max_length=50, null=True, blank=True)
    account_holder_relation_with_dependent = models.CharField(max_length=100, null=True, blank=True)
    account_holder_dob = models.DateField(null=True, blank=True)
    account_holder_nid = models.CharField(max_length=50, null=True, blank=True)
    dummy_field = models.CharField(max_length=50, null=True, blank=True)
    attachments = models.JSONField(null=True, blank=True)
    banking_info = models.ForeignKey(
        "WorkforceEmployeeBankingInfo",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="dependent_employee_banking_info",
    )
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_employee_dependent'


class WorkforceEmployeeAccident(HistoryModel):
    workforce_application = models.ForeignKey(
        "WorkforceApplication",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_employee_accident_application",
    )
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
    rejoin_date = models.DateField(null=True, blank=True)
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


class WorkforceEmployeeAccountInfo(HistoryModel):
    beneficiary_type = models.CharField(max_length=30)
    beneficiary_id = models.CharField(max_length=50)
    on_behalf_of = models.CharField(max_length=30)
    present_location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="dependent_present_location",
    )
    permanent_location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="dependent_permanent_location",
    )
    bank = models.ForeignKey(
        Bank,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="workforce_dependent_bank",
    )
    branch = models.ForeignKey(
        Bank,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_dependent_branch",
    )
    account_holder_name = models.CharField(max_length=255)
    account_owner_name = models.CharField(
        max_length=255, null=True, blank=True)
    account_number = models.CharField(max_length=50)
    status = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_employee_account_info'


class WorkforceApplication(HistoryModel):
    workforce_employee = models.ForeignKey(
        WorkforceEmployee,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_employee",
    )
    workforce_employee_verification = models.CharField(max_length=30, null=True, blank=True)
    workforce_employee_verification_remarks = models.TextField(null=True, blank=True)
    employee_designation_info = models.JSONField(null=True, blank=True)
    employee_document_info = models.JSONField(null=True, blank=True)
    employee_bank_info = models.JSONField(null=True, blank=True)
    employee_bank_info_verification = models.CharField(max_length=30, null=True, blank=True)
    employee_bank_info_verification_remarks = models.TextField(null=True, blank=True)
    employee_dependent_info = models.JSONField(null=True, blank=True)
    employee_dependent_info_verification = models.CharField(max_length=30, null=True, blank=True)
    employee_dependent_info_verification_remarks = models.TextField(null=True, blank=True)
    employee_accident_info = models.JSONField(null=True, blank=True)
    employee_accident_info_verification = models.CharField(max_length=30, null=True, blank=True)
    employee_accident_info_verification_remarks = models.TextField(null=True, blank=True)
    employee_children_info = models.JSONField(null=True, blank=True)
    employee_children_info_verification = models.CharField(max_length=30, null=True, blank=True)
    employee_children_info_verification_remarks = models.TextField(null=True, blank=True)
    applicant_info = models.JSONField(null=True, blank=True)
    applicant_info_verification = models.CharField(max_length=30, null=True, blank=True)
    applicant_info_verification_remarks = models.TextField(null=True, blank=True)
    doctors_entry = models.JSONField(null=True, blank=True)
    doctors_entry_verification = models.CharField(max_length=30, null=True, blank=True)
    doctors_entry_verification_remarks = models.TextField(max_length=30, null=True, blank=True)
    organization = models.ForeignKey(
        WorkforceOrganization,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_application_organization",
    )
    organization_type = models.CharField(max_length=50, null=True, blank=True)
    employee_employer = models.ForeignKey(
        WorkforceEmployer,
        models.DO_NOTHING,
        blank=True,
        null=True
    )
    employee_factory = models.ForeignKey(
        WorkforceFactory,
        models.DO_NOTHING,
        blank=True,
        null=True
    )
    application_type = models.CharField(max_length=50, null=True, blank=True)
    association_type = models.CharField(max_length=50, null=True, blank=True)
    is_submitted = models.BooleanField(null=True, blank=True)
    verified_by = models.CharField(max_length=30, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    tracking_number = models.CharField(max_length=30, null=True, blank=True)
    cf_application_summary = models.ForeignKey(
        "WorkforceApplicationSummary",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="cf_application_summary"
    )
    eis_application_summary = models.ForeignKey(
        "WorkforceApplicationSummary",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="eis_application_summary"
    )
    blwf_application_summary = models.ForeignKey(
        "WorkforceApplicationSummary",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="blwf_application_summary"
    )
    grant_money = models.ForeignKey(
        "WorkforceGrantMoney",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="application_grant_money"
    )
    metadata = models.JSONField(null=True, blank=True)
    metadata_verification = models.CharField(max_length=30, null=True, blank=True)
    metadata_verification_remarks = models.TextField(null=True, blank=True)
    grant_amount = models.CharField(max_length=20, null=True, blank=True)
    submitted_by = models.CharField(max_length=50, null=True, blank=True)
    application_for = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)
    institution_info = models.JSONField(null=True, blank=True)
    institution_info_verification = models.CharField(max_length=30, null=True, blank=True)
    institution_info_verification_remarks = models.TextField(null=True, blank=True)
    last_base_salary = models.CharField(max_length=15, null=True, blank=True)
    doctors_diagnosis = models.CharField(max_length=512, null=True, blank=True)
    doctors_recommended_donation = models.CharField(max_length=15, null=True, blank=True)
    doctors_flag = models.CharField(max_length=30, null=True, blank=True)
    doctors_flag_note = models.CharField(max_length=512, null=True, blank=True)
    eis_payment_type = models.CharField(max_length=50, null=True, blank=True)
    eis_calculated_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    eis_approved_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    eis_initial_monthly_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    eis_monthly_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    pv_factor = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    initial_replacement_rate = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    deceased_worker_info = models.JSONField(null=True, blank=True)
    deceased_worker_info_verification = models.CharField(max_length=30, null=True, blank=True)
    deceased_worker_info_verification_remarks = models.TextField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_applications'


class WorkforceDocumentType(HistoryModel):
    field_id = models.CharField(max_length=500, null=True, blank=True)
    application_type = models.CharField(max_length=500, null=True, blank=True)
    organization_type = models.CharField(max_length=500, null=True, blank=True)
    application_for = models.CharField(max_length=500, null=True, blank=True)
    document_type_no = models.IntegerField(null=True, blank=True)
    document_type = models.CharField(max_length=500, null=True, blank=True)
    document_count = models.CharField(max_length=30, null=True, blank=True)
    name_bn = models.CharField(max_length=500, null=True, blank=True)
    name_en = models.CharField(max_length=500, null=True, blank=True)
    workforce_disease = models.ForeignKey(
        "WorkforceDiseases",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="disease"
    )
    mandatory_for_applicant = models.BooleanField(null=True, blank=True)
    form_step_no = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_document_type'


class WorkforceDocumentMap(HistoryModel):
    workforce_document_type = models.ForeignKey(
        WorkforceDocumentType,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_document_type",
    )
    mapped_by = models.ForeignKey(
        InteractiveUser,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="mapped_by",
    )
    type = models.CharField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_document_map'


class WorkforceUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_bn = models.CharField(max_length=255)
    first_name_en = models.CharField(max_length=255)
    last_name_en = models.CharField(max_length=255, default=" ")
    nid = models.CharField(max_length=30, null=True, blank=True, unique=True)
    birth_certificate_no = models.CharField(
        max_length=30, null=True, blank=True, unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_user'


class WorkforceOtp(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_bn = models.CharField(max_length=255)
    first_name_en = models.CharField(max_length=255)
    last_name_en = models.CharField(max_length=255, default=" ")
    nid = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=20)
    otp = models.CharField(
        max_length=6, default=generate_otp, null=True, blank=True)
    birth_certificate_no = models.CharField(
        max_length=30, null=True, blank=True)
    creation_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(default=expiry_time)
    attempts = models.IntegerField(default=0)
    status = models.CharField(max_length=30, default='active')

    class Meta:
        managed = True
        db_table = 'workforce_otp'


class WorkforceApplicationMovement(HistoryModel):
    application = models.ForeignKey(
        WorkforceApplication,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="application",
    )
    note = models.TextField(null=True, blank=True)
    action = models.CharField(max_length=255, null=True, blank=True)
    to_employee_record = models.ForeignKey(
        WorkforceOrganizationEmployee,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="to_employee_record",
    )
    from_employee_record = models.ForeignKey(
        WorkforceOrganizationEmployee,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="from_employee_record",
    )
    application_from = models.ForeignKey(
        InteractiveUser,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="movement_application_from",
    )
    application_to = models.ForeignKey(
        InteractiveUser,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="movement_application_to",
    )
    deadline_date = models.DateField(null=True, blank=True)
    is_reverted = models.BooleanField(null=True, blank=True)
    reverting_date = models.DateField(null=True, blank=True)
    reverted_by = models.ForeignKey(
        WorkforceOrganizationEmployee,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="reverted_by",
    )
    revert_note = models.TextField(null=True, blank=True)
    from_office_designation = models.ForeignKey(
        WorkforceOrganizationUnitDesignation,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="from_office_designation",
    )
    to_office_designation = models.ForeignKey(
        WorkforceOrganizationUnitDesignation,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="to_office_designation",
    )
    from_role = models.ForeignKey(
        Role,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="from_role",
    )
    to_role = models.ForeignKey(
        Role,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="to_role",
    )
    status = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_application_movement'


class WorkforceApplicationSummary(HistoryModel):
    application_data = models.JSONField(null=True, blank=True)
    meeting_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)
    organization_type = models.CharField(max_length=30, null=True, blank=True)
    section_type = models.CharField(max_length=30, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    month = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_application_summary'


class WorkforceApplicationSummaryMovement(HistoryModel):
    application_summary = models.ForeignKey(
        WorkforceApplicationSummary,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="application_summary",
    )
    comment = models.TextField(null=True, blank=True)
    action = models.CharField(max_length=255, null=True, blank=True)
    from_workforce_organization_employee = models.ForeignKey(
        WorkforceOrganizationEmployee,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="from_workforce_organization_employee"
    )
    to_workforce_organization_employee = models.ForeignKey(
        WorkforceOrganizationEmployee,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="to_workforce_organization_employee"
    )
    is_current = models.BooleanField(null=True, blank=True)
    is_cc = models.BooleanField(null=True, blank=True)
    is_committee_head = models.BooleanField(null=True, blank=True)
    is_committee_member = models.BooleanField(null=True, blank=True)
    deadline_date = models.DateField(null=True, blank=True)
    is_reverted = models.BooleanField(null=True, blank=True)
    reverting_date = models.DateField(null=True, blank=True)
    reverted_by = models.ForeignKey(
        WorkforceOrganizationEmployee,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="summary_reverted_by",
    )
    revert_note = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_application_summary_movement'


class WorkforceGrantMoney(HistoryModel):
    organization_type = models.CharField(max_length=50, null=True, blank=True)
    application_type = models.CharField(max_length=50, null=True, blank=True)
    application_type_name_bn = models.CharField(
        max_length=50, null=True, blank=True)
    application_type_name_en = models.CharField(
        max_length=50, null=True, blank=True)
    grant_money = models.FloatField(null=True, blank=True)
    application_type_no = models.CharField(max_length=2, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_grant_money'


class WorkforceEducation(HistoryModel):
    application = models.ForeignKey(
        WorkforceApplication,
        on_delete=models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="educations",
    )
    workforce_employee = models.ForeignKey(
        WorkforceEmployee,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="educations",
    )
    workforce_dependant = models.ForeignKey(
        WorkforceEmployeeDependent,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="educations",
    )
    education_level = models.CharField(null=True, blank=True)
    applicant_type = models.CharField(null=True, blank=True)
    education_board = models.CharField(null=True, blank=True)
    passing_year = models.IntegerField(null=True, blank=True)
    roll_number = models.CharField(null=True, blank=True)
    registration_number = models.CharField(
        null=True, blank=True)
    result = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    institution = models.CharField(max_length=255, null=True, blank=True)
    child_name_en = models.CharField(max_length=255, null=True, blank=True)
    child_name_bn = models.CharField(max_length=255, null=True, blank=True)
    child_birth_date = models.DateField(null=True, blank=True)
    child_nid_no = models.CharField(max_length=30, null=True, blank=True)
    child_birth_certificate_no = models.CharField(
        max_length=30, null=True, blank=True)
    study_class = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_education'


class WorkforceDiseases(HistoryModel):
    grade = models.CharField(max_length=2)
    disease_type = models.CharField(max_length=512, null=True, blank=True)
    disease_name = models.CharField(max_length=512, null=True, blank=True)
    disease_no = models.CharField(max_length=4, null=True, blank=True)
    documents = models.JSONField(null=True, blank=True)
    minimum_donation_amount = models.FloatField()
    maximum_donation_amount = models.FloatField()
    status = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_diseases'


class WorkforceEmployeeBankingInfo(HistoryModel):
    name_bn = models.CharField(
        max_length=255, null=True, blank=True, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(
        max_length=255, null=True, blank=True, db_comment='English name field')
    account_holder_name = models.CharField(
        max_length=255, null=True, blank=True)
    employee = models.ForeignKey(
        WorkforceEmployee,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="employee_banking_employee_id",
    )
    application = models.ForeignKey(
        "WorkforceApplication",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="employee_banking_info_application",
    )
    dependant = models.ForeignKey(
        WorkforceEmployeeDependent,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="employee_banking_dependents",
    )
    branch = models.ForeignKey(
        Bank,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="workforce_banking_bank",
    )
    type = models.CharField(max_length=255, null=True, blank=True)
    amount = models.CharField(max_length=20, null=True, blank=True)
    account_no = models.CharField(max_length=20, null=True, blank=True)
    bank_account_type = models.CharField(max_length=64, null=True, blank=True)
    nid = models.CharField(max_length=64, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    relation_with_dependent = models.CharField(max_length=64, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)
    account_holder_type = models.CharField(max_length=64, null=True, blank=True)
    parent_dependent = models.ForeignKey(
        WorkforceEmployeeDependent,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="employee_banking_parent_dependent",
    )

    class Meta:
        managed = True
        db_table = 'workforce_employee_banking_info'


class WorkforceFactoryRegistration(models.Model):
    id = models.UUIDField(primary_key=True, db_column="UUID", default=None, editable=False)
    factory = models.ForeignKey(
        WorkforceFactory,
        models.DO_NOTHING,
        blank=True,
        null=True,
    )
    workforce_employer = models.ForeignKey(
        WorkforceEmployer,
        models.DO_NOTHING,
        blank=True,
        null=True,
    )
    employer_id = models.CharField(max_length=255, null=True, blank=True)
    employer_id_lima = models.CharField(max_length=255, null=True, blank=True)
    name_bn = models.CharField(
        max_length=255, null=True, db_comment='Translatable name field. May use any language')
    name_en = models.CharField(max_length=255, db_comment='English name field')
    location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="factory_location"
    )
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)
    is_same_company_representative = models.SmallIntegerField(default=0)
    association_type = models.CharField(max_length=50, null=True, blank=True)

    # Representative (embedded) data
    representative_type = models.CharField(max_length=255)
    representative_name_bn = models.CharField(
        max_length=255, db_comment='Translatable name field. May use any language')
    representative_name_en = models.CharField(max_length=255, db_comment='English name field')
    representative_location = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="representative_location"
    )
    representative_address = models.TextField(null=True, blank=True)
    representative_phone_number = models.CharField(max_length=20, null=True, blank=True)
    representative_email = models.CharField(max_length=255, null=True, blank=True)
    representative_nid = models.CharField(max_length=30, null=True, blank=True)
    representative_passport_no = models.CharField(max_length=30, null=True, blank=True)
    representative_birth_date = models.DateField(null=True, blank=True)
    representative_position = models.CharField(max_length=255, null=True, blank=True)
    representative_status = models.CharField(max_length=30, null=True, blank=True)

    # New approval workflow fields
    modified_by = models.ForeignKey(
        InteractiveUser,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="factory_registration_modified"
    )
    approved_by = models.ForeignKey(
        InteractiveUser,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="factory_registration_approved"
    )
    approval_status = models.CharField(max_length=30, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    date_created = models.DateTimeField(db_column="DateCreated", null=True, default=py_datetime.now)
    date_updated = models.DateTimeField(db_column="DateUpdated", null=True, default=py_datetime.now)

    class Meta:
        managed = True
        db_table = 'workforce_employer_registrable_factories'


class WorkforcePostoffice(models.Model):
    w_code = models.ForeignKey(
        Location,
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="w_code_postoffice",
    )
    post_code = models.CharField(max_length=512, null=True, blank=True)
    post_office = models.CharField(max_length=512, null=True, blank=True)
    name_en = models.CharField(max_length=512, null=True, blank=True)
    name_bn = models.CharField(max_length=512, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_postoffice'


class WorkforceAssociation(HistoryModel):
    office_name_bn = models.CharField(max_length=512, null=True, blank=True)
    office_name_en = models.CharField(max_length=512, null=True, blank=True)
    jurisdiction_locations = models.CharField(max_length=512, null=True, blank=True)
    association_type = models.CharField(max_length=50, null=True, blank=True)
    office_admin = models.ForeignKey(
        WorkforceOrganizationEmployee,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="association_organization_employee",
    )
    status = models.CharField(max_length=30, null=True, blank=True)
    minimum_salary = models.DecimalField(max_digits=25, decimal_places=4, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_association'


class WorkforceEisPaymentProcess(HistoryModel):
    workforce_application = models.ForeignKey(
        "WorkforceApplication",
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="workforce_payment_application",
    )
    workforce_application_summary = models.ForeignKey(
        "WorkforceApplicationSummary",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_payment_application_summary",
    )
    workforce_employee_dependent = models.ForeignKey(
        "WorkforceEmployeeDependent",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_payment_employee_dependent",
    )
    bank = models.ForeignKey(
        Bank,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_payment_bank",
    )

    bank_account_no = models.CharField(max_length=50, null=True, blank=True)
    bank_account_holder_name = models.CharField(max_length=255, null=True, blank=True)

    eis_payment_type = models.CharField(max_length=50, null=True, blank=True)
    eis_calculated_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    eis_approved_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    eis_initial_replacement_rate= models.FloatField(null=True, blank=True)
    eis_initial_monthly_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    eis_monthly_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    increment_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    increment_date= models.DateField(null=True, blank=True)
    decrement_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    decrement_date= models.DateField(null=True, blank=True)
    decrement_end_date= models.DateField(null=True, blank=True)
    total_adjustment_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    month_index = models.IntegerField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    processing_date = models.DateField(null=True, blank=True)
    processed_by = models.ForeignKey(
        InteractiveUser,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_payment_processed_by",
    )
    is_disbursed = models.BooleanField(default=False)
    approved = models.CharField(max_length=10, null=True, blank=True)
    beneficiary_id = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(default="active", max_length=50, null=True, blank=True)
    beneficiary_status = models.CharField(max_length=25, db_comment="hold, closed, eligible", default="eligible")
    reason= models.CharField(max_length=50, db_comment="Remarried, Died, live_check_denied", null=True, blank=True)
    remarks= models.TextField(null=True, blank=True)
    remarriage_or_death_date= models.DateField(null=True, blank=True)
    last_live_check_date = models.DateField(null=True, blank=True)
    live_check_remarks= models.TextField(null=True, blank=True)
    is_eligible = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'workforce_eis_payment_process'


class WorkforceEisPaymentDisbursementStage(HistoryModel):
    workforce_application = models.ForeignKey(
        "WorkforceApplication",
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="workforce_payment_stage_application",
    )
    workforce_application_summary = models.ForeignKey(
        "WorkforceApplicationSummary",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_payment_stage_application_summary",
    )
    workforce_employee_dependent = models.ForeignKey(
        "WorkforceEmployeeDependent",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_payment_stage_employee_dependent",
    )
    bank = models.ForeignKey(
        Bank,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_payment_stage_bank",
    )

    bank_account_no = models.CharField(max_length=50, null=True, blank=True)
    bank_account_holder_name = models.CharField(max_length=255, null=True, blank=True)

    eis_payment_type = models.CharField(max_length=50, null=True, blank=True)
    eis_calculated_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    eis_approved_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    eis_initial_replacement_rate= models.FloatField(null=True, blank=True)
    eis_initial_monthly_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    eis_monthly_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    increment_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    decrement_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    total_adjustment_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    month_index = models.IntegerField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    processing_date = models.DateField(null=True, blank=True)
    processed_by = models.ForeignKey(
        InteractiveUser,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_payment_stage_processed_by",
    )
    is_disbursed = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    approved = models.CharField(max_length=10, null=True, blank=True)
    beneficiary_id = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_eis_payment_disbursement_stage'



class WorkforceEisPaymentDisbursement(HistoryModel):
    workforce_application = models.ForeignKey(
        "WorkforceApplication",
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="workforce_payment_disbursement_application",
    )
    workforce_application_summary = models.ForeignKey(
        "WorkforceApplicationSummary",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_payment_disbursement_application_summary",
    )
    workforce_employee_dependent = models.ForeignKey(
        "WorkforceEmployeeDependent",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_payment_disbursement_employee_dependent",
    )
    bank = models.ForeignKey(
        Bank,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_payment_disbursement_bank",
    )

    bank_account_no = models.CharField(max_length=50, null=True, blank=True)
    bank_account_holder_name = models.CharField(max_length=255, null=True, blank=True)
    eis_payment_type = models.CharField(max_length=50, null=True, blank=True)
    eis_calculated_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    eis_approved_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    eis_initial_replacement_rate= models.FloatField(null=True, blank=True)
    eis_initial_monthly_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    eis_monthly_amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    month_index = models.IntegerField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    disbursement_date = models.DateField(null=True, blank=True)
    disbursed_by = models.ForeignKey(
        InteractiveUser,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="workforce_payment_disbursed_by",
    )

    class Meta:
        managed = True
        db_table = 'workforce_eis_payment_disbursements'


class WorkforceAllAssociation(HistoryModel):
    name_bn = models.CharField(max_length=512, null=True, blank=True)
    name_en = models.CharField(max_length=512, null=True, blank=True)
    address = models.CharField(max_length=512, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    short_name_bn = models.CharField(max_length=50, null=True, blank=True)
    short_name_en = models.CharField(max_length=50, null=True, blank=True)
    web_address = models.CharField(max_length=512, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, blank=True)
    minimum_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    start_date= models.DateField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'workforce_all_association'


class WorkforceOtherCompensationInfo(HistoryModel):
    workforce_application = models.ForeignKey(
        "WorkforceApplication",
        models.DO_NOTHING,
        blank=False,
        null=False,
        related_name="workforce_application_other_compensation_info",
    )

    entry_by = models.CharField(max_length=50, null=True, blank=True, db_comment="factory, officer")
    received_from_organization = models.TextField(null=True, blank=True)
    date_of_compensation = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=25, decimal_places=5, null=True, blank=True)
    status_of_payment = models.CharField(max_length=30, null=True, blank=True, db_comment="paid, unpaid")
    is_eis_benefit_adjustment_eligible = models.CharField(max_length=6, default="No", db_comment="for entry_by officer only, value=yes, no, empty")
    remarks = models.TextField(null=True, blank=True, db_comment="for entry_by officer only")
    payment_type= models.CharField(max_length=50, null=True, blank=True, db_comment="monthly, yearly, one time, installment")


    class Meta:
        managed = True
        db_table = 'workforce_other_compensation_info'
