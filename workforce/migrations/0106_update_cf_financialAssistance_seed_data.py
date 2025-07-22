# On 2025-07-22

from django.db import migrations
from django.conf import settings
import uuid


def seed_updated_document_types(apps, schema_editor):
    WorkforceDocumentType = apps.get_model('workforce', 'WorkforceDocumentType')
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))

    # Get admin user
    user = User.objects.get(username="Admin")
    user_id = user.id

    # Delete data where `organization_type='cf' and application_type='financialAssistance'`
    WorkforceDocumentType.objects.filter(
        organization_type='cf',
        application_type='financialAssistance'
    ).delete()

    data = [
        {
            "id": uuid.uuid4(),
            "document_type_no": 43,
            "application_type": "financialAssistance",
            "organization_type": "cf",
            "application_for": "normal_death",
            "field_id": "financialAssistance_nid_of_deceased_worker",
            "document_type": "nid of deceased worker",
            "document_count": "single",
            "name_bn": "মৃত শ্রমিকের জাতীয় পরিচয়পত্র",
            "name_en": "nid of the deceased worker",
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id
        },
        {
            "id": uuid.uuid4(),
            "document_type_no": 44,
            "application_type": "financialAssistance",
            "organization_type": "cf",
            "application_for": "normal_death",
            "field_id": "financialAssistance_employee_birth_certificate_copy",
            "document_type": "birth cirtificate pf deceased worker",
            "document_count": "single",
            "name_bn": "মৃত শ্রমিকের জন্ম সনদের সত্যায়িত অনুলিপি",
            "name_en": "birth cirtificate pf deceased worker",
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id
        },
        {
            "id": uuid.uuid4(),
            "document_type_no": 45,
            "application_type": "financialAssistance",
            "organization_type": "cf",
            "application_for": "normal_death",
            "field_id": "financialAssistance_Photo_of_deceased_worker",
            "document_type": "Photo of deceased worker",
            "document_count": "single",
            "name_bn": "মৃত শ্রমিকের  ছবি",
            "name_en": "Photo of the dead worker",
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id
        },
        {
            "id": uuid.uuid4(),
            "document_type_no": 46,
            "application_type": "financialAssistance",
            "organization_type": "cf",
            "application_for": "normal_death",
            "field_id": "financialAssistance_appointment_letter_of_deceased_worker",
            "document_type": "appointment letter of deceased worker",
            "document_count": "single",
            "name_bn": "মৃত শ্রমিকের নিয়োগপত্র",
            "name_en": "appointment letter of deceased worker",
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id
        },
        {
            "id": uuid.uuid4(),
            "document_type_no": 47,
            "application_type": "financialAssistance",
            "organization_type": "cf",
            "application_for": "normal_death",
            "field_id": "financialAssistance_deceased_workers_last_six_months_pay_slip",
            "document_type": "Copy of the deceased worker's last six months pay slip",
            "document_count": "single",
            "name_bn": "মৃত শ্রমিকের শেষ ছয় মাসের বেতন শীটের কপি",
            "name_en": "Copy of the deceased worker's last six months' pay slip",
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id
        },
        {
            "id": uuid.uuid4(),
            "document_type_no": 48,
            "application_type": "financialAssistance",
            "organization_type": "cf",
            "application_for": "normal_death",
            "field_id": "financialAssistance_deceased_workers_database_copy",
            "document_type": "Copy of online database of deceased workers",
            "document_count": "single",
            "name_bn": "মৃত শ্রমিকের অনলাইন ডেটাবেজের কপি",
            "name_en": "Copy of online database of deceased workers",
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id
        },
        {
            "id": uuid.uuid4(),
            "document_type_no": 49,
            "application_type": "financialAssistance",
            "organization_type": "cf",
            "application_for": "normal_death",
            "field_id": "financialAssistance_organization_issued_id",
            "document_type": "id card issued by the organization",
            "document_count": "single",
            "name_bn": "প্রতিষ্ঠান কর্তৃক প্রদত্ত আইডি কার্ড",
            "name_en": "id card issued by the organization",
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id
        },
        {
            "id": uuid.uuid4(),
            "document_type_no": 50,
            "application_type": "financialAssistance",
            "organization_type": "cf",
            "application_for": "normal_death",
            "field_id": "financialAssistance_certificate_issued_by_organization",
            "document_type": "certificate issued by the organization (with all the information of the worker)",
            "document_count": "single",
            "name_bn": "প্রতিষ্ঠান কর্তৃক প্রদত্ত প্রত্যয়ন পত্র (শ্রমিকের সকল তথ্যসহ)",
            "name_en": "certificate issued by the organization (with all the information of the worker)",
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id
        },
        {
            "id": uuid.uuid4(),
            "document_type_no": 51,
            "application_type": "financialAssistance",
            "organization_type": "cf",
            "application_for": "normal_death",
            "field_id": "financialAssistance_certificate_issued_by_institution",
            "document_type": "certificate issued by the institution (with all the information of the nominee)",
            "document_count": "single",
            "name_bn": "প্রতিষ্ঠান কর্তৃক প্রদত্ত প্রত্যয়ন পত্র (নমিনীর সকল তথ্যসহ)",
            "name_en": "certificate issued by the institution (with all the information of the nominee)",
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id
        },
        {
            "id": uuid.uuid4(),
            "document_type_no": 52,
            "application_type": "financialAssistance",
            "organization_type": "cf",
            "application_for": "normal_death",
            "field_id": "financialAssistance_organization_membership_certificate",
            "document_type": "organization membership certificate",
            "document_count": "single",
            "name_bn": "প্রতিষ্ঠানের মেম্বারশীপ সনদপত্র",
            "name_en": "organization membership certificate",
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id
        },
        {
            "id": uuid.uuid4(),
            "document_type_no": 53,
            "application_type": "financialAssistance",
            "organization_type": "cf",
            "application_for": "normal_death",
            "field_id": "financialAssistance_death_certificate_main_copy",
            "document_type": "death certificate (main copy)",
            "document_count": "single",
            "name_bn": "রেজিস্টার্ড চিকিৎসক / ইউনিয়ন পরিষদ / পৌরসভা বা সিটি কর্পোরেশন কর্তৃক প্রদত্ত মৃত্যু সনদ (মূলকপি)",
            "name_en": "death certificate (main copy)",
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id
        },
        {
            "id": uuid.uuid4(),
            "document_type_no": 54,
            "application_type": "financialAssistance",
            "organization_type": "cf",
            "application_for": "normal_death",
            "field_id": "financialAssistance_inheritance_certificate_main_copy",
            "document_type": "inheritance certificate (main copy)",
            "document_count": "single",
            "name_bn": "ইউনিয়ন পরিষদ /পৌরসভা বা সিটি কর্পোরেশন হতে ওয়ারিশান সনদ (মূলকপি)",
            "name_en": "inheritance certificate (main copy)",
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id
        },
        {
            "id": uuid.uuid4(),
            "document_type_no": 55,
            "application_type": "financialAssistance",
            "organization_type": "cf",
            "application_for": "normal_death",
            "field_id": "financialAssistance_nominees_nid",
            "document_type": "nominee's nid",
            "document_count": "single",
            "name_bn": "নমিনীর জাতীয় পরিচয়পত্র",
            "name_en": "nominee's national identity card",
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id
        },
        {
            "id": uuid.uuid4(),
            "document_type_no": 56,
            "application_type": "financialAssistance",
            "organization_type": "cf",
            "application_for": "normal_death",
            "field_id": "financialAssistance_nominees_birth_certificate",
            "document_type": "nominee's birth certificate",
            "document_count": "single",
            "name_bn": "নমিনীর জন্মসনদ",
            "name_en": "nominee's birth certificate",
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id
        },
        {
            "id": uuid.uuid4(),
            "document_type_no": 57,
            "application_type": "financialAssistance",
            "organization_type": "cf",
            "application_for": "normal_death",
            "field_id": "financialAssistance_nominees_photo",
            "document_type": "nominee's photo",
            "document_count": "single",
            "name_bn": "নমিনীর ছবি",
            "name_en": "nominee's photo",
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id
        },
        {
            "id": uuid.uuid4(),
            "document_type_no": 58,
            "application_type": "financialAssistance",
            "organization_type": "cf",
            "application_for": "normal_death",
            "field_id": "financialAssistance_nominees_bank_statement",
            "document_type": "copy of the nominee's bank account check or statement",
            "document_count": "single",
            "name_bn": "নমিনীর ব্যাংক হিসাবের চেক বা স্টেটমেন্টের কপি",
            "name_en": "copy of the nominee's bank account check or statement",
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id
        },
        {
            "id": uuid.uuid4(),
            "document_type_no": 59,
            "application_type": "financialAssistance",
            "organization_type": "cf",
            "application_for": "accidental_death",
            "field_id": "financialAssistance_deceased_workers_accidental_color_photo",
            "document_type": "workers accidental color photo",
            "document_count": "single",
            "name_bn": "শ্রমিকের দুর্ঘটনার রঙিন ছবি",
            "name_en": "photo of deceased worker",
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id
        }
    ]

    for item in data:
        WorkforceDocumentType.objects.create(**item)


class Migration(migrations.Migration):

    dependencies = [
        ('workforce', '0105_alter_historicalworkforceeducation_applicant_type_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_updated_document_types),
    ]
