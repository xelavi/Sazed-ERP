"""
Restaura els FK constraints de provider_id a purchases_purchaseinvoice i
purchases_purchasequotedoc apuntant a customers_customer.

La migració 0006 va eliminar els FK constraints via SQL raw (que apuntaven a
providers_provider) per evitar violacions de FK durant la migració de dades.
La migració 0007 era AlterField però PostgreSQL la va detectar com a no-op
perquè la columna ja existia. Aquesta migració afegeix explícitament els
constraints que han de quedar com a part de l'esquema final.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0005_remove_quote_model'),
        ('purchases', '0007_switch_provider_fk_to_customer'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE purchases_purchaseinvoice
                    ADD CONSTRAINT purchases_purchasein_provider_id_fk_customers
                    FOREIGN KEY (provider_id)
                    REFERENCES customers_customer(id)
                    DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE purchases_purchasequotedoc
                    ADD CONSTRAINT purchases_purchasequ_provider_id_fk_customers
                    FOREIGN KEY (provider_id)
                    REFERENCES customers_customer(id)
                    DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
                ALTER TABLE purchases_purchaseinvoice
                    DROP CONSTRAINT IF EXISTS purchases_purchasein_provider_id_fk_customers;

                ALTER TABLE purchases_purchasequotedoc
                    DROP CONSTRAINT IF EXISTS purchases_purchasequ_provider_id_fk_customers;
            """,
        ),
    ]
