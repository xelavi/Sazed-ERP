from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0002_purchasequotedoc_purchasequotedocline'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseinvoice',
            name='odoo_id',
            field=models.PositiveIntegerField(
                blank=True, db_index=True, null=True,
                help_text='ID del account.move (in_invoice) asociado en Odoo.',
            ),
        ),
    ]
