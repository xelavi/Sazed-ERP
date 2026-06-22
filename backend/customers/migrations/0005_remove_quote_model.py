from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0004_customer_prestashop_id'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Quote',
        ),
    ]
