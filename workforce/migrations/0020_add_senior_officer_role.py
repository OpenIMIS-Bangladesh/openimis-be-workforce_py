from django.db import migrations
import uuid
from core.models import Role

from datetime import datetime as py_datetime


def add_senior_officer_role_instance(apps, schema_editor):
    senior_officer_role_instance = Role(
        uuid=uuid.uuid4(),
        name="Senior Officer",
        is_system=0,
        is_blocked=False,
        audit_user_id=-1
    )
    senior_officer_role_instance.save()


class Migration(migrations.Migration):
    dependencies = [
        ('workforce', '0019_workforcedocument_historicalworkforcedocument'),
    ]

    operations = [
        migrations.RunPython(add_senior_officer_role_instance),
    ]
