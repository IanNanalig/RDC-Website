from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("projects", "0018_alter_project_ai_priority_level"),
    ]

    operations = [
        migrations.CreateModel(
            name="AIProjectScoreReview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("score", models.FloatField()),
                ("grade", models.CharField(max_length=20)),
                ("summary", models.TextField(blank=True, default="")),
                ("justification", models.TextField(blank=True, default="")),
                ("negative_matches", models.JSONField(blank=True, default=list)),
                ("risk_flags", models.JSONField(blank=True, default=list)),
                ("extracted_fields", models.JSONField(blank=True, default=dict)),
                ("progress_assessment", models.TextField(blank=True, default="")),
                ("raw_result", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ai_score_reviews",
                        to="projects.project",
                    ),
                ),
                (
                    "reviewed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
