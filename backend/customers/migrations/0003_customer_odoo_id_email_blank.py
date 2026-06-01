from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0002_customer_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=254),
        ),
        migrations.AddField(
            model_name='customer',
            name='odoo_id',
            field=models.PositiveIntegerField(
                blank=True, db_index=True, null=True,
                help_text='ID del res.partner asociado en Odoo (si está sincronizado).',
            ),
        ),
    ]
