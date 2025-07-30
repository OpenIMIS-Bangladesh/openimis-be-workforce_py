from django.db import migrations
import json
import os


def load_geo_data(apps, schema_editor):
    schema_editor.execute('TRUNCATE TABLE "tblLocations" CASCADE')

    Location = apps.get_model('location', 'Location')
    db_alias = schema_editor.connection.alias

    current_dir = os.path.dirname(__file__)
    json_path = os.path.join(current_dir, "geo_data.json")

    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        parent_id = int(item["ParentLocationId"]) if item["ParentLocationId"] != "0" else None
        zip_code_w_id = int(item["wCodeId"]) if item["wCodeId"] != "0" else None

        Location.objects.using(db_alias).create(
            id=int(item["LocationId"]),
            uuid=item["LocationUUID"],
            parent_id=parent_id,
            zip_code_w_id_id=zip_code_w_id,
            type=item["LocationType"],
            code=item["LocationCode"],
            name=item["LocationName"]
        )


class Migration(migrations.Migration):

    dependencies = [
        ('workforce', '0124_historicalworkforceapplication_applicant_info_and_more'),
    ]

    operations = [
        migrations.RunPython(load_geo_data),
    ]
