from django.db import migrations


def remove_legacy_auth_user_metadata(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Permission = apps.get_model("auth", "Permission")
    legacy_content_types = ContentType.objects.filter(
        app_label="auth",
        model="user",
    )
    Permission.objects.filter(content_type__in=legacy_content_types).delete()
    legacy_content_types.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            remove_legacy_auth_user_metadata,
            migrations.RunPython.noop,
        ),
    ]
