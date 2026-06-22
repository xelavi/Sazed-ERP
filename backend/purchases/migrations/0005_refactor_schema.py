"""
Refactoring de l'app purchases:
- Elimina PurchaseSeries i PurchaseQuote (models legacy)
- Elimina la FK 'series' de PurchaseInvoice
- Afegeix FK 'company' directa a PurchaseInvoice (multitenença sense JOIN)
- Elimina inline tax_percent/tax_amount de PurchaseQuoteDocLine
- Afegeix PurchaseQuoteDocLineTax
"""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('core', '0002_saleschannel_company_tag_company_taxrate_company_and_more'),
        ('products', '0003_add_reorder_rule'),
        ('purchases', '0004_purchaseinvoice_is_template_recurringpurchaseinvoice'),
    ]

    operations = [
        # 1. Elimina la constraint de número únic que depèn de series
        migrations.RemoveConstraint(
            model_name='purchaseinvoice',
            name='unique_purchase_invoice_number_per_series',
        ),

        # 2. Elimina la FK series de PurchaseInvoice
        migrations.RemoveField(
            model_name='purchaseinvoice',
            name='series',
        ),

        # 3. Afegeix FK company directa a PurchaseInvoice
        migrations.AddField(
            model_name='purchaseinvoice',
            name='company',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='purchase_invoices',
                to='accounts.company',
            ),
        ),

        # 4. Elimina PurchaseSeries
        migrations.DeleteModel(name='PurchaseSeries'),

        # 5. Elimina PurchaseQuote (la FK de PurchaseQuote apunta a providers.Provider;
        #    es buida el model abans d'eliminar Provider)
        migrations.DeleteModel(name='PurchaseQuote'),

        # 6. Elimina inline tax_percent i tax_amount de PurchaseQuoteDocLine
        migrations.RemoveField(
            model_name='purchasequotedocline',
            name='tax_percent',
        ),
        migrations.RemoveField(
            model_name='purchasequotedocline',
            name='tax_amount',
        ),

        # 7. Crea PurchaseQuoteDocLineTax
        migrations.CreateModel(
            name='PurchaseQuoteDocLineTax',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tax_name', models.CharField(max_length=50)),
                ('tax_percent', models.DecimalField(decimal_places=2, max_digits=5)),
                ('is_retention', models.BooleanField(default=False)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('quote_line', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='taxes',
                    to='purchases.purchasequotedocline',
                )),
                ('tax_rate', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    to='core.taxrate',
                )),
            ],
        ),
    ]
