# Generated by Django 3.0.3 on 2020-06-21 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_l', models.CharField(max_length=10, verbose_name='業態カテゴリ')),
                ('name', models.CharField(max_length=30, verbose_name='業態名')),
            ],
        ),
        migrations.CreateModel(
            name='Pref',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pref', models.CharField(max_length=6, verbose_name='都道府県コード')),
                ('name', models.CharField(max_length=10, verbose_name='都道府県名')),
            ],
        ),
    ]
