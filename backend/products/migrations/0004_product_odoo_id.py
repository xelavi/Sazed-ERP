from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_add_reorder_rule'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='odoo_id',
            field=models.PositiveIntegerField(
                blank=True, db_index=True, null=True,
                help_text='ID del product.product asociado en Odoo (si está sincronizado).',
            ),
        ),
    ]
