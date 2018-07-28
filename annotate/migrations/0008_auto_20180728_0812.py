# Generated by Django 2.0.7 on 2018-07-28 12:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('annotate', '0007_auto_20180728_0810'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='root',
        ),
        migrations.AddField(
            model_name='projectfile',
            name='parentproject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='annotate.Project'),
        ),
        migrations.AlterField(
            model_name='projectfile',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='annotate.ProjectDirectory'),
        ),
    ]