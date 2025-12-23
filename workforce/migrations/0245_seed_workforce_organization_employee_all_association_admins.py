# Custom migration on 2025-12-23
import uuid
import datetime
from django.db import migrations
from django.conf import settings


def seed_interactive_users_and_employees_for_all_association_admin(apps, schema_editor):
    WorkforceAllAssociation = apps.get_model('workforce', 'WorkforceAllAssociation')
    WorkforceOrganizationEmployee = apps.get_model('workforce', 'WorkforceOrganizationEmployee')
    InteractiveUser = apps.get_model('core', 'InteractiveUser')
    Role = apps.get_model('core', 'Role')
    UserRole = apps.get_model('core', 'UserRole')
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))

    admin_user = User.objects.filter(username="Admin").first()
    role_instance = Role.objects.get(name='esi_association_admin')

    def create_interactive_user(last_name, other_names, login_name, role_id):
        interactive_user = InteractiveUser.objects.create(
            language_id="fr",
            last_name=last_name,
            other_names=other_names,
            login_name=login_name,
            audit_user_id=1,
            role_id=role_id,
            private_key="C1C224B03CD9BC7B6A86D77F5DACE40191766C485CD55DC48CAF9AC873335D6F",
            password="59E66831C680C19E8736751D5480A7C3291BD8775DF47C19C4D0361FBC1C3438",
        )

        # Create core User
        user_core = User.objects.create(
            username=interactive_user.login_name,
            i_user_id=interactive_user.id,
        )

        # Create UserRole (skip if already exists)
        if not UserRole.objects.filter(user_id=interactive_user.id, role_id=role_id).exists():
            UserRole.objects.create(
                user_id=interactive_user.id,
                role_id=role_id,
                validity_from=datetime.date.today(),
                audit_user_id=1,
            )

        return interactive_user

    def generate_login_name(short_name):
        if short_name == "Tea Association of Bangladesh":
            return "TAB_admin"

        name = (short_name.strip()).replace(" ", "")
        association_admin_login_name = name + "_admin"

        return association_admin_login_name

    associations = WorkforceAllAssociation.objects.all()

    for assoc in associations:
        name_bn = assoc.name_bn.strip()
        name_en = assoc.name_en.strip()
        short_name_en = assoc.short_name_en.strip()
        login_name = generate_login_name(short_name_en)

        if InteractiveUser.objects.filter(login_name=login_name).exists():
            continue

        user = create_interactive_user(
            last_name=name_en,
            other_names=name_bn,
            login_name=login_name,
            role_id=role_instance.id,
        )

        WorkforceOrganizationEmployee.objects.create(
            id=uuid.uuid4(),
            name_bn=name_bn,
            name_en=name_en,
            related_user_id=user.id,
            status="active",
            user_created_id=admin_user.id,
            user_updated_id=admin_user.id,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('workforce', '0244_seed_all_association_data'),
    ]

    operations = [
        migrations.RunPython(
            seed_interactive_users_and_employees_for_all_association_admin,
        ),
    ]
