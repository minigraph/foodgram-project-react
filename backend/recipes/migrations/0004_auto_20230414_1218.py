# Generated by Django 2.2.19 on 2023-04-14 12:18

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20230408_1704'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(help_text='Цвет тега', max_length=7, validators=[django.core.validators.RegexValidator('#[a-fA-F0–9]{6}', 'Недопустимые символы в коде цвета!')], verbose_name='Цвет'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(help_text='Название тега', max_length=200, unique=True, validators=[django.core.validators.RegexValidator('[-+\\w\\s]+', 'Недопустимые символы в имени!')], verbose_name='Имя'),
        ),
    ]
