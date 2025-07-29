from django.db import migrations


def delete_users_and_employees(apps, schema_editor):
    WorkforceUser = apps.get_model('workforce', 'WorkforceUser')
    WorkforceEmployee = apps.get_model('workforce', 'WorkforceEmployee')

    WorkforceUser.objects.all().delete()
    WorkforceEmployee.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('workforce', '0120_alter_bank_location_alter_bank_parent_and_more'),
    ]

    operations = [
        migrations.RunPython(delete_users_and_employees),
    ]
