import django_filters
from django.db.models import Q

from .models import Customer


class CustomerFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    contact_type = django_filters.ChoiceFilter(
        field_name='contact_type', choices=Customer.ContactType.choices,
    )
    status = django_filters.ChoiceFilter(choices=Customer.Status.choices)
    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains')

    class Meta:
        model = Customer
        fields = ['contact_type', 'status', 'city']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(email__icontains=value)
            | Q(vat_id__icontains=value)
        ).distinct()
