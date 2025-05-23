# Generated by Django 5.2 on 2025-05-01 05:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0017_remove_sale_box_quantity_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='saleitem',
            name='total_cost_value',
        ),
        migrations.AlterField(
            model_name='saleitem',
            name='sale',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='inventory.sale', verbose_name='Sale'),
        ),
    ]
