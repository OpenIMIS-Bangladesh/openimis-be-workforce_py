from django.db import migrations
import uuid
from django.conf import settings


def seed_grant_money(apps, schema_editor):
    WorkforceGrantMoney = apps.get_model('workforce', 'WorkforceGrantMoney')
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    user = User.objects.get(username="Admin")
    user_id = user.id

    data = [
        {
            "id": uuid.uuid4(),
            "organization_type": "cf",
            "application_type": "medicalAssistance",
            "grant_money": 20000,
            "status": "active",
            "user_created_id": user_id,
            "user_updated_id": user_id,
        },
        {
            "id": uuid.uuid4(),
            "organization_type": "blwf",
            "application_type": "medicalAssistance",
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
        ('workforce', '0079_historicalworkforceapplication_metadata_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_grant_money),
    ]
