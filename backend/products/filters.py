import django_filters
from django.db.models import Q

from .models import Product


class ProductFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    status = django_filters.ChoiceFilter(choices=Product.Status.choices)
    product_type = django_filters.ChoiceFilter(
        field_name='product_type', choices=Product.ProductType.choices,
    )
    category = django_filters.CharFilter(field_name='category__name')
    channel = django_filters.CharFilter(method='filter_channel')

    class Meta:
        model = Product
        fields = ['status', 'product_type', 'category']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(sku__icontains=value)
            | Q(category__name__icontains=value)
            | Q(suppliers__supplier__name__icontains=value)
        ).distinct()

    def filter_channel(self, queryset, name, value):
        return queryset.filter(channels__name=value)
