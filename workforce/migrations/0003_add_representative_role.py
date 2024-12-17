from django.db import migrations
import uuid
from core.models import Role

from datetime import datetime as py_datetime


def add_representative_role_instance(apps, schema_editor):
    representative_role_instance = Role(
        uuid=uuid.uuid4(),
        name="WORKFORCE REPRESENTATIVE",
        is_system=800,
        is_blocked=False,
        audit_user_id=-1
    )
    representative_role_instance.save()


class Migration(migrations.Migration):
    dependencies = [
        ('workforce', '0002_rename_workforce_employer_id_historicalworkforcefactory_workforce_employer_and_more'),
    ]

    operations = [
        migrations.RunPython(add_representative_role_instance),
    ]
