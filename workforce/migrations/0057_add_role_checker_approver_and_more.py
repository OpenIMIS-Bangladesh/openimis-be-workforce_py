from django.db import migrations
import uuid
from core.models import Role

from datetime import datetime as py_datetime


def add_checker_and_approver_role(apps, schema_editor):
    checker_role = Role(
        uuid=uuid.uuid4(),
        name="Checker",
        is_system=0,
        is_blocked=False,
        audit_user_id=-1
    )
    checker_role.save()

    approver_role = Role(
        uuid=uuid.uuid4(),
        name="Approver",
        is_system=0,
        is_blocked=False,
        audit_user_id=-1
    )
    approver_role.save()


class Migration(migrations.Migration):
    dependencies = [
        ('workforce', '0056_workforceotp'),
    ]

    operations = [
        migrations.RunPython(add_checker_and_approver_role),
    ]
