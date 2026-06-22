import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_saleschannel_company_tag_company_taxrate_company_and_more'),
        ('invoices', '0008_invoice_prestashop_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quoteline',
            name='tax_percent',
        ),
        migrations.RemoveField(
            model_name='quoteline',
            name='tax_amount',
        ),
        migrations.CreateModel(
            name='QuoteLineTax',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tax_name', models.CharField(max_length=50)),
                ('tax_percent', models.DecimalField(decimal_places=2, max_digits=5)),
                ('is_retention', models.BooleanField(default=False)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('quote_line', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='taxes',
                    to='invoices.quoteline',
                )),
                ('tax_rate', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    to='core.taxrate',
                )),
            ],
        ),
    ]
