# Generated by Django 4.2.16 on 2024-12-17 09:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workforce', '0003_add_representative_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workforceorganizationunit',
            name='workforce_representative',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='workforce.workforcerepresentative'),
        ),
    ]
