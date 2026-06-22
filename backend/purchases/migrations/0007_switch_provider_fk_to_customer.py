"""
Canvia la FK provider de PurchaseInvoice i PurchaseQuoteDoc
de providers.Provider a customers.Customer.
Després de la migració de dades (0006), els provider_id ja apunten
a IDs de Customer, de manera que AlterField només actualitza el constraint.
"""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0005_remove_quote_model'),
        ('purchases', '0006_migrate_providers_to_customers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseinvoice',
            name='provider',
            field=models.ForeignKey(
                limit_choices_to={'is_supplier': True},
                on_delete=django.db.models.deletion.PROTECT,
                related_name='purchase_invoices',
                to='customers.customer',
            ),
        ),
        migrations.AlterField(
            model_name='purchasequotedoc',
            name='provider',
            field=models.ForeignKey(
                limit_choices_to={'is_supplier': True},
                on_delete=django.db.models.deletion.PROTECT,
                related_name='purchase_quote_docs',
                to='customers.customer',
            ),
        ),
    ]
