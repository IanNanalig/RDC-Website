from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0017_ai_priority_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="ai_priority_level",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
