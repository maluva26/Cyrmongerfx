import uuid
from datetime import timedelta

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils import timezone


def seed_demo_messages(apps, schema_editor):
    CommunityMessage = apps.get_model("community", "CommunityMessage")
    if CommunityMessage.objects.exists():
        return

    now = timezone.now()
    demo_messages = [
        ("Mandla FX", "London session is clean today. Watching EURUSD around the previous high.", 18),
        ("Aisha Charts", "Risk first. I am keeping it at 1% until NY opens.", 15),
        ("Neo Scalps", "Gold is moving fast. Wait for the retest before chasing.", 12),
        ("Cyrmonger Desk", "Educational reminder: no signal is guaranteed. Journal the reason before entry.", 9),
        ("Lebo Swing", "GBPJPY gave a nice structure break on M15.", 6),
        ("Tariq Trader", "Anyone checking US30? Spread looks better now.", 3),
    ]

    CommunityMessage.objects.bulk_create(
        [
            CommunityMessage(
                author_name=author,
                body=body,
                created_at=now - timedelta(minutes=minutes_ago),
            )
            for author, body, minutes_ago in demo_messages
        ]
    )


def remove_demo_messages(apps, schema_editor):
    CommunityMessage = apps.get_model("community", "CommunityMessage")
    CommunityMessage.objects.filter(user__isnull=True).delete()


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CommunityMessage",
            fields=[
                ("message_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("author_name", models.CharField(max_length=120)),
                ("body", models.TextField(blank=True)),
                ("image", models.ImageField(blank=True, null=True, upload_to="community-chat/%Y/%m/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="community_messages",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "community_message",
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["-created_at"], name="community_m_created_5c3ac7_idx"),
                    models.Index(fields=["user", "-created_at"], name="community_m_user_id_b0a08e_idx"),
                ],
            },
        ),
        migrations.RunPython(seed_demo_messages, remove_demo_messages),
    ]
