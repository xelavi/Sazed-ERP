import django_filters
from django.db.models import Q

from .models import Provider


class ProviderFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    contact_type = django_filters.ChoiceFilter(
        field_name='contact_type', choices=Provider.ContactType.choices,
    )
    status = django_filters.ChoiceFilter(choices=Provider.Status.choices)
    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains')

    class Meta:
        model = Provider
        fields = ['contact_type', 'status', 'city']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(email__icontains=value)
            | Q(vat_id__icontains=value)
        ).distinct()
