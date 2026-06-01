from django.db import migrations, models


def backfill_invoice_company(apps, schema_editor):
    """Rellena Invoice.company a partir de customer.company o series.company."""
    Invoice = apps.get_model('invoices', 'Invoice')
    for inv in Invoice.objects.select_related('customer', 'series').iterator():
        company_id = (
            getattr(inv.customer, 'company_id', None)
            or getattr(inv.series, 'company_id', None)
        )
        if company_id and inv.company_id != company_id:
            inv.company_id = company_id
            inv.save(update_fields=['company'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_systemsettings'),
        ('invoices', '0005_quote_quoteline'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='company',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=models.deletion.CASCADE,
                related_name='invoices',
                to='accounts.company',
            ),
        ),
        migrations.AddField(
            model_name='invoice',
            name='odoo_id',
            field=models.PositiveIntegerField(
                blank=True, db_index=True, null=True,
                help_text='ID del account.move asociado en Odoo (si está sincronizado).',
            ),
        ),
        migrations.RunPython(backfill_invoice_company, noop_reverse),
    ]
