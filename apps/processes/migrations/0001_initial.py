# Generated by Django 3.2.9 on 2022-08-05 01:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('objects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('state', models.BooleanField(default=True, verbose_name='Estado')),
                ('created_date', models.DateField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('modified_date', models.DateField(auto_now=True, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateField(auto_now=True, verbose_name='Fecha de Eliminación')),
                ('description', models.CharField(max_length=50, verbose_name='Description')),
                ('object_process', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='objects.object', verbose_name='object_process')),
            ],
            options={
                'verbose_name': 'Process',
                'verbose_name_plural': 'Processes',
            },
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('state', models.BooleanField(default=True, verbose_name='Estado')),
                ('created_date', models.DateField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('modified_date', models.DateField(auto_now=True, verbose_name='Fecha de Modificación')),
                ('deleted_date', models.DateField(auto_now=True, verbose_name='Fecha de Eliminación')),
                ('description', models.CharField(max_length=50, verbose_name='Description')),
                ('code', models.CharField(max_length=50, verbose_name='Code of Activity')),
                ('sort', models.IntegerField(verbose_name='Order of Activity')),
                ('process_activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='processes.process', verbose_name='process_activity')),
            ],
            options={
                'verbose_name': 'Activity',
                'verbose_name_plural': 'Activities',
            },
        ),
    ]