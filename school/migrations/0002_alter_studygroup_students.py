# Reconstructed from the successful migration name shown in the conversation.
# Replace with the exact locally generated 0002 file if possible.
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("school", "0001_initial")]
    operations = [
        migrations.AlterField(
            model_name="studygroup",
            name="students",
            field=models.ManyToManyField(
                related_name="study_groups",
                through="school.Enrollment",
                to="school.studentprofile",
                verbose_name="Ученики",
            ),
        ),
    ]
