# Generated by Django 5.1.7 on 2025-04-17 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('freshmart', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sold_quantity',
            field=models.IntegerField(default=0, verbose_name='Sold Quantity'),
        ),
    ]
