from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0005_seed_city_identities_and_enforce_cascade"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="is_ticketed",
            field=models.BooleanField(null=True),
        ),
    ]
