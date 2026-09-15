import django.contrib.contenttypes.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="DispatchSecret",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reference", models.CharField(max_length=80)),
                ("checksum", models.CharField(max_length=24)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="DeskVisit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("url", models.URLField(max_length=500)),
                ("claimed", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("slug", models.SlugField(unique=True)),
                ("summary", models.TextField(blank=True)),
                ("approved", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="GenericNote",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("object_id", models.PositiveIntegerField()),
                ("body", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("content_type", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="contenttypes.contenttype")),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "indexes": [
                    models.Index(fields=["content_type", "object_id"], name="core_generi_content_8b36a9_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="DeliveryRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("payload", models.TextField()),
                ("released", models.BooleanField(default=False)),
                ("project", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to="core.project")),
            ],
        ),
        migrations.CreateModel(
            name="ReviewTicket",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160)),
                ("preview_token", models.CharField(max_length=64, unique=True)),
                ("state", models.CharField(default="queued", max_length=32)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.project")),
            ],
        ),
        migrations.CreateModel(
            name="AssetTag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("label", models.CharField(max_length=80)),
                ("color", models.CharField(default="slate", max_length=24)),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.project")),
            ],
        ),
        migrations.CreateModel(
            name="AuditLine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event", models.CharField(max_length=160)),
                ("reference", models.CharField(max_length=80)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.project")),
            ],
        ),
        migrations.CreateModel(
            name="ContactCard",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("display_name", models.CharField(max_length=120)),
                ("mailbox", models.EmailField(max_length=254)),
                ("public", models.BooleanField(default=True)),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.project")),
            ],
        ),
        migrations.CreateModel(
            name="NotificationDraft",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("subject", models.CharField(max_length=160)),
                ("body", models.TextField()),
                ("active", models.BooleanField(default=False)),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.project")),
            ],
        ),
        migrations.CreateModel(
            name="RoutingEnvelope",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("label", models.CharField(max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("secret", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to="core.dispatchsecret")),
            ],
        ),
        migrations.CreateModel(
            name="DeskRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("private_body", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("envelope", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to="core.routingenvelope")),
                ("reviewer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ("ticket", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.reviewticket")),
            ],
        ),
    ]
