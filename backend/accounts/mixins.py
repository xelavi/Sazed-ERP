"""
Base mixin for company-scoped viewsets.

All data viewsets should inherit from CompanyMixin to:
1. Filter querysets to the active company
2. Auto-set the company FK on create
"""

from rest_framework.permissions import IsAuthenticated


class CompanyMixin:
    """
    Mixin for ViewSets that scopes data to request.company.

    Usage:
        class ProductViewSet(CompanyMixin, viewsets.ModelViewSet):
            queryset = Product.objects.all()
            ...
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'company') and self.request.company:
            return qs.filter(company=self.request.company)
        return qs.none()

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def perform_update(self, serializer):
        serializer.save()
