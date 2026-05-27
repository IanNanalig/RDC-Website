from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0016_alter_useractivity_event"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="ai_priority_score",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="project",
            name="ai_priority_level",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="project",
            name="ai_analysis_notes",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="project",
            name="ai_analyzed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
