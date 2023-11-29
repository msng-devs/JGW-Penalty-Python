# Generated by Django 4.2.3 on 2023-11-29 07:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0002_alter_member_options_alter_role_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="member",
            name="email",
            field=models.EmailField(
                db_column="MEMBER_EMAIL", max_length=255, unique=True
            ),
        ),
        migrations.AlterField(
            model_name="member",
            name="id",
            field=models.CharField(
                db_column="MEMBER_PK", max_length=28, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="member",
            name="name",
            field=models.CharField(db_column="MEMBER_NM", max_length=45),
        ),
        migrations.AlterField(
            model_name="member",
            name="role",
            field=models.ForeignKey(
                db_column="ROLE_ROLE_PK",
                on_delete=django.db.models.deletion.CASCADE,
                to="common.role",
            ),
        ),
        migrations.AlterField(
            model_name="member",
            name="status",
            field=models.BooleanField(db_column="MEMBER_STATUS", default=True),
        ),
        migrations.AlterField(
            model_name="role",
            name="id",
            field=models.AutoField(
                db_column="ROLE_PK", primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="role",
            name="name",
            field=models.CharField(db_column="ROLE_NM", max_length=45, unique=True),
        ),
    ]