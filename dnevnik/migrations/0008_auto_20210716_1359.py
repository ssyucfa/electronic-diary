# Generated by Django 3.2.5 on 2021-07-16 10:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import dnevnik.models


class Migration(migrations.Migration):

    dependencies = [
        ('dnevnik', '0007_alter_user_managers'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['first_name', 'last_name']},
        ),
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', dnevnik.models.UserManager()),
            ],
        ),
        migrations.RemoveField(
            model_name='studyclass',
            name='teacher',
        ),
        migrations.RemoveField(
            model_name='user',
            name='teacher',
        ),
        migrations.AddField(
            model_name='studyclass',
            name='is_teacher',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='class_for_teacher', to=settings.AUTH_USER_MODEL, verbose_name='Учитель'),
        ),
    ]