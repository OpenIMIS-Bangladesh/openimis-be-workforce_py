# Generated by Django 4.2.16 on 2024-12-17 16:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workforce', '0004_alter_workforceorganizationunit_workforce_representative'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalworkforceorganizationunit',
            name='workforce_representative',
        ),
        migrations.RemoveField(
            model_name='workforceorganizationunit',
            name='workforce_representative',
        ),
    ]
