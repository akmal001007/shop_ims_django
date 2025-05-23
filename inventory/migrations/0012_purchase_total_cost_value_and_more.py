# Generated by Django 5.2 on 2025-04-27 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0011_remove_purchase_total_cost_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='total_cost_value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Total Cost'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='cost_per_item',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Cost per Item'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='items_per_package',
            field=models.IntegerField(blank=True, null=True, verbose_name='Items per Package'),
        ),
    ]
