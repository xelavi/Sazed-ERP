"""
Assigna les factures de compra existents a l'empresa Sazed i les ajusta
perquè el benefici final (venda - compra) sigui positiu i realista (~28% marge).

Estratègia:
  - Total venda Sazed (sense Voided): ~596.127€
  - Objectiu benefici net: ~28% → compres objectiu = 596.127 * 0.72 ≈ 429.211€
  - Les 139 factures de compra orfes sumen 333.709€ → ja estan per sota!
    Simplement les assignem a Sazed (sense tocar imports) → marge ~44%.
  - Per fer-ho més realista, n'ajustem algunes d'addicionals per arribar
    a ~430.000€ de compra (marge ~28%).
"""
from decimal import Decimal
from accounts.models import Company
from invoices.models import Invoice
from purchases.models import PurchaseInvoice

sazed = Company.objects.get(name='Sazed')

# ── 1. Total venda actual ──────────────────────────────────────────
total_venda = Decimal(str(round(
    sum(float(i.total_amount) for i in Invoice.objects.filter(company=sazed).exclude(status='Voided')),
    2
)))
print(f"Total venda Sazed: {total_venda:.2f}€")

# ── 2. Assignar totes les factures de compra orfes a Sazed ────────
orphans = PurchaseInvoice.objects.filter(company__isnull=True)
count_assigned = orphans.count()
orphans.update(company=sazed)
print(f"Factures de compra assignades a Sazed: {count_assigned}")

# ── 3. Comprovar la situació resultant ─────────────────────────────
purchases = PurchaseInvoice.objects.filter(company=sazed).exclude(status='Voided')
total_compra = Decimal(str(round(
    sum(float(i.total_amount) for i in purchases),
    2
)))
print(f"Total compra Sazed: {total_compra:.2f}€")

benefici_actual = total_venda - total_compra
marge_actual = (benefici_actual / total_venda * 100) if total_venda else 0
print(f"Benefici brut: {benefici_actual:.2f}€ ({marge_actual:.1f}% marge)")

# ── 4. Ajustar per arribar a ~28% de marge ────────────────────────
# Objectiu: compra total = venda * 0.72
objectiu_compra = total_venda * Decimal('0.72')
diferencia = objectiu_compra - total_compra

print(f"\nObjectiu compra (72% vendes): {objectiu_compra:.2f}€")
print(f"Diferència a afegir: {diferencia:.2f}€")

if diferencia > 0:
    # Cal augmentar la despesa: escalar proporcionalment totes les factures orfes recents
    # (les que acabem d'assignar), amb un factor uniforme
    factor = float(objectiu_compra) / float(total_compra)
    print(f"Factor d'escala: {factor:.4f}")

    updated = 0
    for inv in purchases:
        if float(inv.total_amount) > 0:
            nou_total = round(float(inv.total_amount) * factor, 2)
            nou_subtotal = round(nou_total / 1.21, 2)  # treu IVA 21%
            nou_iva = round(nou_total - nou_subtotal, 2)
            inv.total_amount = Decimal(str(nou_total))
            inv.subtotal = Decimal(str(nou_subtotal))
            inv.tax_base = Decimal(str(nou_subtotal))
            inv.total_tax = Decimal(str(nou_iva))
            inv.balance_due = max(Decimal('0'), inv.total_amount - inv.paid_amount)
            inv.save(update_fields=['total_amount', 'subtotal', 'tax_base', 'total_tax', 'balance_due'])
            updated += 1

    print(f"Factures actualitzades: {updated}")
else:
    print("Les compres ja superen l'objectiu, no cal ajustar.")

# ── 5. Resum final ────────────────────────────────────────────────
purchases_final = PurchaseInvoice.objects.filter(company=sazed).exclude(status='Voided')
total_compra_final = Decimal(str(round(
    sum(float(i.total_amount) for i in purchases_final), 2
)))
benefici_final = total_venda - total_compra_final
marge_final = (benefici_final / total_venda * 100) if total_venda else 0

print(f"\n{'='*50}")
print(f"  Total vendes:  {total_venda:>12.2f}€")
print(f"  Total compres: {total_compra_final:>12.2f}€")
print(f"  Benefici net:  {benefici_final:>12.2f}€  ({marge_final:.1f}% marge)")
print(f"{'='*50}")
