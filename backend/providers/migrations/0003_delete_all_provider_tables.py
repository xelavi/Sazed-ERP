"""
Elimina totes les taules de l'app providers.
Els Providers ja han estat migrats a customers.Customer (is_supplier=True)
per la migració purchases/0006.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('providers', '0002_provider_odoo_id'),
        ('purchases', '0007_switch_provider_fk_to_customer'),
    ]

    operations = [
        migrations.DeleteModel(name='PurchaseOrder'),
        migrations.DeleteModel(name='ProviderActivity'),
        migrations.DeleteModel(name='ProviderNote'),
        migrations.DeleteModel(name='Provider'),
    ]
