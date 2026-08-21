from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("users", "0016_rename_legacy_user_table")]

    operations = [
        migrations.CreateModel(
            name="RequestThrottle",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("scope", models.CharField(max_length=40)),
                ("key_hash", models.CharField(max_length=64)),
                ("window_started_at", models.DateTimeField()),
                ("count", models.PositiveIntegerField(default=1)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
            ],
            options={
                "db_table": "REQUEST_THROTTLE",
                "constraints": [
                    models.UniqueConstraint(
                        fields=("scope", "key_hash"),
                        name="uq_request_throttle_scope_key",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("count__gte", 1)),
                        name="ck_request_throttle_positive_count",
                    ),
                ],
            },
        )
    ]
