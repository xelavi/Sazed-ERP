from django.db import migrations


def zero_existing_prices(apps, schema_editor):
    """Pone a 0 los precios de productos ya existentes que estén sin valor.

    A partir de ahora cada producto tiene un precio explícito (que puede ser 0)
    y ese precio se usa al añadirlo a presupuestos y facturas. Para no complicar
    la migración, los productos antiguos sin precio quedan a 0 €.
    """
    Product = apps.get_model('products', 'Product')
    Product.objects.filter(price__isnull=True).update(price=0)
    Product.objects.filter(price_excl_tax__isnull=True).update(price_excl_tax=0)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_product_odoo_id'),
    ]

    operations = [
        migrations.RunPython(zero_existing_prices, noop),
    ]
