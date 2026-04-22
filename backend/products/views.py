from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.mixins import CompanyMixin
from .models import (
    Category, Product, StockMovement, ProductVariant,
    ProductAttribute, ProductAttributeValue,
)
from .serializers import (
    CategorySerializer,
    ProductListSerializer, ProductDetailSerializer, ProductWriteSerializer,
    StockMovementSerializer, ProductVariantSerializer,
    ProductAttributeSerializer,
)
from .filters import ProductFilter


class CategoryViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ['name']
    pagination_class = None


class ProductViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset = Product.objects.select_related(
        'category', 'tax_rate', 'warehouse',
    ).prefetch_related(
        'tags', 'channels', 'variants', 'suppliers',
    ).all()
    filterset_class = ProductFilter
    ordering_fields = ['name', 'sku', 'price', 'stock', 'updated_at', 'created_at']
    ordering = ['-updated_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return ProductWriteSerializer
        return ProductDetailSerializer

    def destroy(self, request, *args, **kwargs):
        """Soft delete: marcar como Archived en lugar de borrar."""
        product = self.get_object()
        product.status = 'Archived'
        product.save(update_fields=['status'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ---------- Nested routes ----------

    @action(detail=True, methods=['get', 'post'], url_path='stock-movements')
    def stock_movements(self, request, pk=None):
        product = self.get_object()
        if request.method == 'GET':
            movements = product.stock_movements.all()
            serializer = StockMovementSerializer(movements, many=True)
            return Response(serializer.data)
        # POST
        serializer = StockMovementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'])
    def variants(self, request, pk=None):
        product = self.get_object()
        if request.method == 'GET':
            variants = product.variants.all()
            serializer = ProductVariantSerializer(variants, many=True)
            return Response(serializer.data)
        # POST
        serializer = ProductVariantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'])
    def attributes(self, request, pk=None):
        product = self.get_object()
        if request.method == 'GET':
            attrs = product.attributes.all()
            serializer = ProductAttributeSerializer(attrs, many=True)
            return Response(serializer.data)
        # POST — expects {name, values: [str, str]}
        attr_serializer = ProductAttributeSerializer(data=request.data)
        attr_serializer.is_valid(raise_exception=True)
        attr = attr_serializer.save(product=product)
        # Create values if provided
        values = request.data.get('values', [])
        for i, val in enumerate(values):
            ProductAttributeValue.objects.create(
                attribute=attr, value=val, position=i,
            )
        return Response(
            ProductAttributeSerializer(attr).data,
            status=status.HTTP_201_CREATED,
        )
