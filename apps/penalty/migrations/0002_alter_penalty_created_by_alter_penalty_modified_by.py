# Generated by Django 4.2.3 on 2023-08-20 14:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("member", "0002_remove_member_created_by_remove_member_modified_by"),
        ("penalty", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="penalty",
            name="created_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)s_created_by",
                to="member.member",
            ),
        ),
        migrations.AlterField(
            model_name="penalty",
            name="modified_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)s_modified_by",
                to="member.member",
            ),
        ),
    ]
