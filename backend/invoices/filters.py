import django_filters
from datetime import date

from django.db.models import Q

from .models import Invoice


class InvoiceFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    status = django_filters.CharFilter(method='filter_status')
    customer = django_filters.NumberFilter(field_name='customer__id')
    series = django_filters.CharFilter(field_name='series__prefix')
    date_from = django_filters.DateFilter(
        field_name='issue_date', lookup_expr='gte',
    )
    date_to = django_filters.DateFilter(
        field_name='issue_date', lookup_expr='lte',
    )
    invoice_type = django_filters.ChoiceFilter(
        choices=Invoice.InvoiceType.choices,
    )

    class Meta:
        model = Invoice
        fields = ['status', 'customer', 'series', 'invoice_type']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(number__icontains=value)
            | Q(customer__name__icontains=value)
        ).distinct()

    def filter_status(self, queryset, name, value):
        if value == 'overdue':
            return queryset.filter(
                status__in=['Approved', 'PartiallyPaid'],
                due_date__lt=date.today(),
            )
        return queryset.filter(status=value)
