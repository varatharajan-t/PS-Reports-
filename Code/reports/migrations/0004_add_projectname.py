from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0003_add_documenttype"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectName",
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
                (
                    "project_definition",
                    models.CharField(
                        db_index=True,
                        help_text="The unique project definition code (e.g., 'NL-C-MN1-001').",
                        max_length=50,
                        unique=True,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="The full name of the project.",
                        max_length=255,
                    ),
                ),
                (
                    "unit",
                    models.CharField(
                        blank=True,
                        help_text="The unit code derived from the project definition (positions 6-8).",
                        max_length=10,
                    ),
                ),
            ],
            options={
                "verbose_name": "Project Name",
                "verbose_name_plural": "Project Names",
                "ordering": ["project_definition"],
            },
        ),
    ]
