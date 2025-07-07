from django.db import migrations, models
import uuid
from django.conf import settings

def reset_and_seed_grant_money(apps, schema_editor):
    WorkforceGrantMoney = apps.get_model('workforce', 'WorkforceGrantMoney')
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    user = User.objects.get(username="Admin")
    user_id = user.id

    # Truncate the table (deletes all rows)
    schema_editor.execute('TRUNCATE TABLE workforce_grant_money RESTART IDENTITY CASCADE')

    data = [
        {
            "id": uuid.uuid4(),
            "organization_type": "cf",
            "application_type": "medicalAssistance",
            "application_type_no": "01",
            "grant_money": 20000,
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id,
        },
        {
            "id": uuid.uuid4(),
            "organization_type": "cf",
            "application_type": "disabilityAssistance",
            "application_type_no": "02",
            "grant_money": 200000,
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id,
        },
        {
            "id": uuid.uuid4(),
            "organization_type": "cf",
            "application_type": "scholarship",
            "application_type_no": "03",
            "grant_money": 20000,
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id,
        },
        {
            "id": uuid.uuid4(),
            "organization_type": "cf",
            "application_type": "financialAssistance",
            "application_type_no": "04",
            "grant_money": 200000,
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id,
        },
        {
            "id": uuid.uuid4(),
            "organization_type": "blwf",
            "application_type": "maternityGrant",
            "application_type_no": "05",
            "grant_money": 25000,
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id,
        },
        {
            "id": uuid.uuid4(),
            "organization_type": "blwf",
            "application_type": "educationGrant",
            "application_type_no": "06",
            "grant_money": 20000,
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id,
        },
        {
            "id": uuid.uuid4(),
            "organization_type": "blwf",
            "application_type": "deadlyGrant",
            "application_type_no": "07",
            "grant_money": 25000,
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id,
        },
        {
            "id": uuid.uuid4(),
            "organization_type": "blwf",
            "application_type": "medicalDonation",
            "application_type_no": "08",
            "grant_money": 20000,
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id,
        }
    ]

    for item in data:
        WorkforceGrantMoney.objects.create(**item)


class Migration(migrations.Migration):

    dependencies = [
        ('workforce', '0082_historicalworkforceapplication_employee_children_info_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalworkforcegrantmoney',
            name='application_type_no',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='workforcegrantmoney',
            name='application_type_no',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.RunPython(reset_and_seed_grant_money),
    ]
