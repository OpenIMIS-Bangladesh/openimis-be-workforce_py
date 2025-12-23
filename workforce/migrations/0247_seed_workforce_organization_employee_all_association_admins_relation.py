# Custom migration on 2025-12-23
from django.db import migrations


def seed_interactive_users_and_employees_for_all_association_admin(apps, schema_editor):
    WorkforceAllAssociation = apps.get_model('workforce', 'WorkforceAllAssociation')
    WorkforceOrganizationEmployee = apps.get_model('workforce', 'WorkforceOrganizationEmployee')

    associations = WorkforceAllAssociation.objects.all()

    for assoc in associations:
        name_en = assoc.name_en.strip()
        employee = WorkforceOrganizationEmployee.objects.filter(name_en=name_en).first()

        if employee:
            employee.all_association_id = assoc.id
            employee.save()


class Migration(migrations.Migration):
    dependencies = [
        ('workforce', '0246_remove_historicalworkforceallassociation_association_admin_and_more'),
    ]

    operations = [
        migrations.RunPython(
            seed_interactive_users_and_employees_for_all_association_admin,
        ),
    ]
