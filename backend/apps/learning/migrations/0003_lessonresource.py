import django.db.models.deletion
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("learning", "0002_lesson_template_key"),
    ]

    operations = [
        migrations.CreateModel(
            name="LessonResource",
            fields=[
                ("resource_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=200)),
                ("kind", models.CharField(choices=[("VIDEO", "YouTube video"), ("LINK", "External link"), ("FILE", "Learning file")], max_length=12)),
                ("url", models.URLField(blank=True, max_length=500)),
                ("file", models.FileField(blank=True, upload_to="learning_materials/%Y/%m")),
                ("original_filename", models.CharField(blank=True, max_length=255)),
                ("content_type", models.CharField(blank=True, max_length=127)),
                ("size_bytes", models.PositiveBigIntegerField(default=0)),
                ("order_index", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("lesson", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="resources", to="learning.lesson")),
            ],
            options={
                "db_table": "lesson_resource",
                "ordering": ["order_index", "created_at"],
                "indexes": [models.Index(fields=["lesson", "order_index"], name="lesson_reso_lesson__762ac2_idx")],
            },
        ),
    ]
