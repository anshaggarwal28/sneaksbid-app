# Generated by Django 4.2.10 on 2024-03-17 23:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sneaksbid', '0013_payment_stripe_charge_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='payment_method',
        ),
    ]
