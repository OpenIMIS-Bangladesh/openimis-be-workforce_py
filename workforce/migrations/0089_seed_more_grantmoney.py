from django.db import migrations
import uuid
from django.conf import settings


def add_more_grant_money(apps, schema_editor):
    WorkforceGrantMoney = apps.get_model('workforce', 'WorkforceGrantMoney')
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))

    try:
        user = User.objects.get(username="Admin")
    except User.DoesNotExist:
        return

    WorkforceGrantMoney.objects.create(
        id=uuid.uuid4(),
        organization_type="cf",
        application_type="maternityGrant",
        grant_money=25000,
        status="active",
        application_type_no="09",
        user_created_id=user.id,
        user_updated_id=user.id,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('workforce', '0088_seed_workforcediseases'),  # Replace with the latest migration file name
    ]

    operations = [
        migrations.RunPython(add_more_grant_money),
    ]
