from django.db import migrations
import json
import os


def load_postoffice_data(apps, schema_editor):
    WorkforcePostoffice = apps.get_model("workforce", "WorkforcePostoffice")
    Location = apps.get_model("location", "Location")
    db_alias = schema_editor.connection.alias

    schema_editor.execute('TRUNCATE TABLE "workforce_postoffice" CASCADE')
    current_dir = os.path.dirname(__file__)
    json_path = os.path.join(current_dir, "postoffice_data.json")

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        w_code_val = item.get("w_code")

        try:
            # match by primary key (LocationId)
            w_code_fk = Location.objects.using(db_alias).get(id=int(w_code_val))
        except (Location.DoesNotExist, ValueError, TypeError):
            # Skip if no matching Location found or invalid value
            continue

        WorkforcePostoffice.objects.using(db_alias).create(
            id=int(item["id"]),
            w_code=w_code_fk,
            post_code=item.get("post_code"),
            # post_office=item.get("post_code"),
            name_en=item.get("name_en"),
            name_bn=item.get("name_bn"),
            status="active",
        )


class Migration(migrations.Migration):

    dependencies = [
        ("workforce", "0168_alter_historicalworkforceemployee_marital_status_and_more"),
    ]

    operations = [
        migrations.RunPython(load_postoffice_data),
    ]
