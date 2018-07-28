# Generated by Django 2.0.7 on 2018-07-28 12:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('annotate', '0006_auto_20180728_0809'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='root',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='annotate.ProjectDirectory'),
        ),
        migrations.AlterField(
            model_name='projectdirectory',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='annotate.ProjectDirectory'),
        ),
    ]
