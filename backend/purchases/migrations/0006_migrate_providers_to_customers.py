"""
Migració de dades: copia els Provider existents com a Customer(is_supplier=True)
i actualitza les FKs de PurchaseInvoice i PurchaseQuoteDoc.

Primer elimina les FK constraints de provider_id (que apuntaven a providers_provider),
fa la migració de dades, i deixa les columnes com a integers bruts fins que
la migració 0007 afegeixi les noves FK constraints a customers_customer.
"""
from django.db import migrations


def drop_provider_fk_constraints(cursor):
    """Elimina dinàmicament les FK constraints de provider_id sense necessitar el nom exacte."""
    for table in ('purchases_purchaseinvoice', 'purchases_purchasequotedoc'):
        cursor.execute("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_schema = 'public'
              AND table_name = %s
              AND constraint_type = 'FOREIGN KEY'
              AND constraint_name LIKE '%%provider%%'
        """, [table])
        for (constraint_name,) in cursor.fetchall():
            cursor.execute(f'ALTER TABLE {table} DROP CONSTRAINT IF EXISTS "{constraint_name}"')


def copy_providers_to_customers(apps, schema_editor):
    # 1. Elimina les FK constraints perquè podem posar IDs de Customer
    with schema_editor.connection.cursor() as cursor:
        drop_provider_fk_constraints(cursor)

    Provider = apps.get_model('providers', 'Provider')
    Customer = apps.get_model('customers', 'Customer')

    # Mapa: provider_id → customer_id
    provider_to_customer = {}

    for prov in Provider.objects.all():
        existing = None
        if prov.vat_id:
            existing = Customer.objects.filter(
                vat_id=prov.vat_id, is_supplier=True,
            ).first()

        if existing:
            provider_to_customer[prov.pk] = existing.pk
        else:
            cust = Customer.objects.create(
                name=prov.name,
                contact_type=prov.contact_type,
                email=prov.email,
                phone=prov.phone,
                website=prov.website,
                status=prov.status,
                vat_id=prov.vat_id,
                legal_name=prov.legal_name,
                address=prov.address,
                city=prov.city,
                province=prov.province,
                postal_code=prov.postal_code,
                country=prov.country,
                payment_method=prov.payment_method,
                bank_account=prov.bank_account,
                avatar_color=prov.avatar_color,
                initials=prov.initials,
                internal_notes=prov.internal_notes,
                is_customer=False,
                is_supplier=True,
                company=prov.company,
            )
            provider_to_customer[prov.pk] = cust.pk

    # 2. Actualitza PurchaseInvoice.provider_id
    PurchaseInvoice = apps.get_model('purchases', 'PurchaseInvoice')
    for inv in PurchaseInvoice.objects.all():
        new_id = provider_to_customer.get(inv.provider_id)
        if new_id and new_id != inv.provider_id:
            PurchaseInvoice.objects.filter(pk=inv.pk).update(provider_id=new_id)

    # 3. Actualitza PurchaseQuoteDoc.provider_id
    PurchaseQuoteDoc = apps.get_model('purchases', 'PurchaseQuoteDoc')
    for doc in PurchaseQuoteDoc.objects.all():
        new_id = provider_to_customer.get(doc.provider_id)
        if new_id and new_id != doc.provider_id:
            PurchaseQuoteDoc.objects.filter(pk=doc.pk).update(provider_id=new_id)


def reverse_migration(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0004_customer_prestashop_id'),
        ('providers', '0002_provider_odoo_id'),
        ('purchases', '0005_refactor_schema'),
    ]

    operations = [
        migrations.RunPython(
            copy_providers_to_customers,
            reverse_migration,
        ),
    ]
