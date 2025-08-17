from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ("services", "0004_donationcenter_alter_blooddonation_options_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name="event",
                    name="blood_donation_fk",
                    field=models.OneToOneField(
                        to="services.blooddonation",
                        null=True, blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event",
                    ),
                ),
            ],
        ),
    ]