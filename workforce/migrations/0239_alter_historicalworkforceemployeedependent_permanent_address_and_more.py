from django.db import migrations, models


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('workforce', '0238_historicalworkforcefactory_minimum_salary_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                UPDATE workforce_employee_dependent
                SET present_address = NULL
                WHERE present_address = '';

                UPDATE workforce_employee_dependent
                SET permanent_address = NULL
                WHERE permanent_address = '';

                UPDATE workforce_historicalworkforceemployeedependent
                SET present_address = NULL
                WHERE present_address = '';

                UPDATE workforce_historicalworkforceemployeedependent
                SET permanent_address = NULL
                WHERE permanent_address = '';

                UPDATE workforce_employee_dependent
                SET present_address =
                    REPLACE(
                        REPLACE(present_address, '''', '"'),
                        'None',
                        'null'
                    )
                WHERE present_address IS NOT NULL;

                UPDATE workforce_employee_dependent
                SET permanent_address =
                    REPLACE(
                        REPLACE(permanent_address, '''', '"'),
                        'None',
                        'null'
                    )
                WHERE permanent_address IS NOT NULL;

                UPDATE workforce_historicalworkforceemployeedependent
                SET present_address =
                    REPLACE(
                        REPLACE(present_address, '''', '"'),
                        'None',
                        'null'
                    )
                WHERE present_address IS NOT NULL;

                UPDATE workforce_historicalworkforceemployeedependent
                SET permanent_address =
                    REPLACE(
                        REPLACE(permanent_address, '''', '"'),
                        'None',
                        'null'
                    )
                WHERE permanent_address IS NOT NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),

        migrations.AlterField(
            model_name='historicalworkforceemployeedependent',
            name='permanent_address',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicalworkforceemployeedependent',
            name='present_address',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='workforceemployeedependent',
            name='permanent_address',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='workforceemployeedependent',
            name='present_address',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
