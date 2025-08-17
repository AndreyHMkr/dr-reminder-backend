from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("services", "0005_event_blood_donation_fk"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="event",
            name="blood_donation",
        ),
        migrations.RenameField(
            model_name="event",
            old_name="blood_donation_fk",
            new_name="blood_donation",
        ),
    ]