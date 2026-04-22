"""Inventory dashboard API — warehouse stats, stock overview, reorder rules."""

from datetime import timedelta

from django.db.models import (
    Sum, Count, Q, F, Value, CharField,
    IntegerField, DecimalField, Case, When,
    ExpressionWrapper,
)
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from products.models import Product, StockMovement, ReorderRule


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_overview(request):
    """
    Global inventory KPIs and per-warehouse breakdown.

    Returns:
      - global_stats: total_products, total_stock, low_stock_count, out_of_stock_count, total_value
      - warehouses: list with id, name, product_count, total_stock, low_stock, value
      - movement_summary: last 30d counts by type (In/Out/Adjust/Return)
      - stock_distribution: top categories by stock
    """
    company = getattr(request, 'company', None)

    products = Product.objects.filter(
        product_type='Product', status='Active',
    )
    if company:
        products = products.filter(company=company)

    def _stock_value():
        return ExpressionWrapper(F('stock') * F('cost'), output_field=DecimalField())

    # ── Global stats ─────────────────────────────────
    agg = products.aggregate(
        total_products=Count('id'),
        total_stock=Coalesce(Sum('stock'), 0),
        total_value=Coalesce(Sum(_stock_value()), 0, output_field=DecimalField()),
    )

    low_stock = products.filter(
        stock__isnull=False,
        min_stock__isnull=False,
        stock__gt=0,
        stock__lte=F('min_stock'),
    ).count()

    out_of_stock = products.filter(
        Q(stock__isnull=True) | Q(stock__lte=0),
    ).count()

    global_stats = {
        'total_products': agg['total_products'],
        'total_stock': agg['total_stock'],
        'total_value': float(agg['total_value'] or 0),
        'low_stock_count': low_stock,
        'out_of_stock_count': out_of_stock,
    }

    # ── Per-warehouse breakdown ──────────────────────
    from core.models import Warehouse
    warehouses_qs = Warehouse.objects.filter(active=True)
    if company:
        warehouses_qs = warehouses_qs.filter(company=company)

    warehouse_data = []
    for wh in warehouses_qs:
        wh_products = products.filter(warehouse=wh)
        wh_agg = wh_products.aggregate(
            count=Count('id'),
            total_stock=Coalesce(Sum('stock'), 0),
            value=Coalesce(Sum(_stock_value()), 0, output_field=DecimalField()),
        )
        wh_low = wh_products.filter(
            stock__isnull=False, min_stock__isnull=False,
            stock__gt=0, stock__lte=F('min_stock'),
        ).count()

        warehouse_data.append({
            'id': wh.id,
            'name': wh.name,
            'address': wh.address,
            'product_count': wh_agg['count'],
            'total_stock': wh_agg['total_stock'],
            'low_stock': wh_low,
            'value': float(wh_agg['value'] or 0),
        })

    # Unassigned products (no warehouse)
    unassigned = products.filter(warehouse__isnull=True)
    un_agg = unassigned.aggregate(
        count=Count('id'),
        total_stock=Coalesce(Sum('stock'), 0),
        value=Coalesce(Sum(_stock_value()), 0, output_field=DecimalField()),
    )
    if un_agg['count'] > 0:
        warehouse_data.append({
            'id': None,
            'name': 'Sin asignar',
            'address': '',
            'product_count': un_agg['count'],
            'total_stock': un_agg['total_stock'],
            'low_stock': 0,
            'value': float(un_agg['value'] or 0),
        })

    # ── Movement summary (last 30 days) ──────────────
    since = timezone.now() - timedelta(days=30)
    movements_qs = StockMovement.objects.filter(created_at__gte=since)
    if company:
        movements_qs = movements_qs.filter(product__company=company)

    movement_summary = list(
        movements_qs.values('movement_type').annotate(
            count=Count('id'),
            total_qty=Coalesce(Sum('quantity'), 0),
        ).order_by('movement_type')
    )

    # ── Stock distribution by category ───────────────
    stock_by_category = list(
        products.filter(stock__isnull=False, stock__gt=0)
        .values(category_name=Coalesce('category__name', Value('Sin categoría')))
        .annotate(
            total_stock=Sum('stock'),
            product_count=Count('id'),
        )
        .order_by('-total_stock')[:8]
    )

    return Response({
        'global_stats': global_stats,
        'warehouses': warehouse_data,
        'movement_summary': movement_summary,
        'stock_by_category': stock_by_category,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def warehouse_stock(request, warehouse_id):
    """
    Stock detail for a specific warehouse.
    Returns products with their stock, min_stock, reorder info.
    """
    company = getattr(request, 'company', None)

    products = Product.objects.filter(
        product_type='Product', status='Active',
    )
    if company:
        products = products.filter(company=company)

    if warehouse_id == 0:
        # Unassigned
        products = products.filter(warehouse__isnull=True)
    else:
        products = products.filter(warehouse_id=warehouse_id)

    items = products.annotate(
        stock_status=Case(
            When(Q(stock__isnull=True) | Q(stock__lte=0), then=Value('out_of_stock')),
            When(stock__lte=F('min_stock'), then=Value('low')),
            default=Value('ok'),
            output_field=CharField(),
        ),
    ).values(
        'id', 'sku', 'name', 'stock', 'reserved', 'min_stock',
        'reorder_point', 'cost', 'stock_status',
        'category__name',
    ).order_by(
        Case(
            When(stock_status='out_of_stock', then=Value(0)),
            When(stock_status='low', then=Value(1)),
            default=Value(2),
            output_field=IntegerField(),
        ),
        'name',
    )

    return Response(list(items))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reorder_rules(request):
    """List all reorder rules for the company."""
    company = getattr(request, 'company', None)
    rules = ReorderRule.objects.select_related('product', 'warehouse')
    if company:
        rules = rules.filter(product__company=company)

    data = [
        {
            'id': r.id,
            'product_id': r.product_id,
            'product_name': r.product.name,
            'product_sku': r.product.sku,
            'product_stock': r.product.stock,
            'warehouse_id': r.warehouse_id,
            'warehouse_name': r.warehouse.name,
            'min_stock': r.min_stock,
            'reorder_qty': r.reorder_qty,
            'max_stock': r.max_stock,
            'enabled': r.enabled,
            'needs_reorder': (
                r.enabled
                and r.product.stock is not None
                and r.product.stock <= r.min_stock
            ),
            'last_triggered': r.last_triggered,
        }
        for r in rules
    ]

    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_reorder_rule(request):
    """Create or update a reorder rule."""
    product_id = request.data.get('product_id')
    warehouse_id = request.data.get('warehouse_id')
    min_stock = request.data.get('min_stock')
    reorder_qty = request.data.get('reorder_qty')
    max_stock = request.data.get('max_stock')
    enabled = request.data.get('enabled', True)

    if not all([product_id, warehouse_id, min_stock, reorder_qty]):
        return Response(
            {'detail': 'product_id, warehouse_id, min_stock and reorder_qty are required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    rule, created = ReorderRule.objects.update_or_create(
        product_id=product_id,
        warehouse_id=warehouse_id,
        defaults={
            'min_stock': min_stock,
            'reorder_qty': reorder_qty,
            'max_stock': max_stock,
            'enabled': enabled,
        },
    )

    return Response({
        'id': rule.id,
        'created': created,
        'product_id': rule.product_id,
        'warehouse_id': rule.warehouse_id,
        'min_stock': rule.min_stock,
        'reorder_qty': rule.reorder_qty,
        'max_stock': rule.max_stock,
        'enabled': rule.enabled,
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restock_product(request):
    """
    Quick restock: create an 'In' StockMovement and update product stock.
    """
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity')

    if not product_id or not quantity or int(quantity) <= 0:
        return Response(
            {'detail': 'product_id and positive quantity are required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {'detail': 'Product not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    quantity = int(quantity)

    StockMovement.objects.create(
        product=product,
        movement_type='In',
        quantity=quantity,
        document_ref=f'RESTOCK-{timezone.now().strftime("%Y%m%d%H%M")}',
        user=request.user.email,
        notes=request.data.get('notes', 'Reabastecimiento manual'),
    )

    product.stock = (product.stock or 0) + quantity
    product.save(update_fields=['stock'])

    return Response({
        'product_id': product.id,
        'new_stock': product.stock,
        'movement_qty': quantity,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def adjust_stock(request):
    """
    Adjust stock: add, remove, or set to a specific value.
    Creates an 'Adjust' movement with reason.
    """
    product_id = request.data.get('product_id')
    adjustment_type = request.data.get('adjustment_type')  # 'add', 'remove', 'set'
    quantity = request.data.get('quantity')
    reason = request.data.get('reason', '')
    notes = request.data.get('notes', '')

    if not product_id or quantity is None:
        return Response(
            {'detail': 'product_id and quantity are required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

    quantity = int(quantity)
    old_stock = product.stock or 0

    if adjustment_type == 'add':
        new_stock = old_stock + quantity
        movement_qty = quantity
    elif adjustment_type == 'remove':
        new_stock = max(old_stock - quantity, 0)
        movement_qty = min(quantity, old_stock)
    elif adjustment_type == 'set':
        new_stock = max(quantity, 0)
        movement_qty = abs(new_stock - old_stock)
    else:
        return Response({'detail': 'Invalid adjustment_type.'}, status=status.HTTP_400_BAD_REQUEST)

    note_text = f'[{reason}] {notes}'.strip() if reason else notes

    StockMovement.objects.create(
        product=product,
        movement_type='Adjust',
        quantity=movement_qty,
        document_ref=f'ADJ-{timezone.now().strftime("%Y%m%d%H%M")}',
        user=request.user.email,
        notes=note_text,
    )

    product.stock = new_stock
    product.save(update_fields=['stock'])

    return Response({
        'product_id': product.id,
        'old_stock': old_stock,
        'new_stock': new_stock,
        'adjustment': new_stock - old_stock,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer_stock(request):
    """
    Transfer stock between warehouses.
    Creates an OUT movement from source and an IN movement to destination.
    """
    product_id = request.data.get('product_id')
    from_warehouse_id = request.data.get('from_warehouse_id')
    to_warehouse_id = request.data.get('to_warehouse_id')
    quantity = request.data.get('quantity')
    notes = request.data.get('notes', '')

    if not all([product_id, from_warehouse_id, to_warehouse_id, quantity]):
        return Response(
            {'detail': 'product_id, from_warehouse_id, to_warehouse_id, and quantity are required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if int(from_warehouse_id) == int(to_warehouse_id):
        return Response(
            {'detail': 'Source and destination warehouse must be different.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

    from core.models import Warehouse
    try:
        from_wh = Warehouse.objects.get(id=from_warehouse_id)
        to_wh = Warehouse.objects.get(id=to_warehouse_id)
    except Warehouse.DoesNotExist:
        return Response({'detail': 'Warehouse not found.'}, status=status.HTTP_404_NOT_FOUND)

    quantity = int(quantity)
    ref = f'TRF-{timezone.now().strftime("%Y%m%d%H%M")}'

    StockMovement.objects.create(
        product=product,
        movement_type='Out',
        quantity=quantity,
        document_ref=ref,
        user=request.user.email,
        notes=f'Transfer to {to_wh.name}. {notes}'.strip(),
    )

    StockMovement.objects.create(
        product=product,
        movement_type='In',
        quantity=quantity,
        document_ref=ref,
        user=request.user.email,
        notes=f'Transfer from {from_wh.name}. {notes}'.strip(),
    )

    return Response({
        'product_id': product.id,
        'quantity': quantity,
        'from_warehouse': from_wh.name,
        'to_warehouse': to_wh.name,
        'reference': ref,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_stock(request):
    """
    All products with stock info for the inventory stock table.
    Supports optional warehouse and status filters via query params.
    """
    company = getattr(request, 'company', None)
    products = Product.objects.filter(product_type='Product', status='Active')
    if company:
        products = products.filter(company=company)

    warehouse_id = request.query_params.get('warehouse')
    if warehouse_id:
        if warehouse_id == '0':
            products = products.filter(warehouse__isnull=True)
        else:
            products = products.filter(warehouse_id=warehouse_id)

    status_filter = request.query_params.get('stock_status')

    items = products.annotate(
        stock_status=Case(
            When(Q(stock__isnull=True) | Q(stock__lte=0), then=Value('out_of_stock')),
            When(stock__lte=F('min_stock'), then=Value('low')),
            default=Value('ok'),
            output_field=CharField(),
        ),
    ).values(
        'id', 'sku', 'name', 'stock', 'reserved', 'min_stock',
        'cost', 'stock_status', 'category__name',
        'warehouse__id', 'warehouse__name',
    ).order_by(
        Case(
            When(stock_status='out_of_stock', then=Value(0)),
            When(stock_status='low', then=Value(1)),
            default=Value(2),
            output_field=IntegerField(),
        ),
        'name',
    )

    if status_filter and status_filter != 'all':
        items = items.filter(stock_status=status_filter)

    return Response(list(items))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def movement_history(request):
    """Recent stock movements across all products."""
    company = getattr(request, 'company', None)
    limit = int(request.query_params.get('limit', 50))

    qs = StockMovement.objects.select_related('product').order_by('-created_at')
    if company:
        qs = qs.filter(product__company=company)

    movements = qs[:limit]
    data = [
        {
            'id': m.id,
            'product_id': m.product_id,
            'product_name': m.product.name,
            'product_sku': m.product.sku,
            'movement_type': m.movement_type,
            'quantity': m.quantity,
            'document_ref': m.document_ref,
            'user': m.user,
            'notes': m.notes,
            'created_at': m.created_at.isoformat(),
        }
        for m in movements
    ]

    return Response(data)
