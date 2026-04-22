"""
Middleware that injects the active company into request.company.

Every authenticated request must include either:
  1. An X-Company header with the company ID, OR
  2. The user's default company (from Membership.is_default=True)

This makes all views automatically company-aware.
"""

from django.http import JsonResponse

from .models import Membership


class CompanyMiddleware:
    """
    Sets request.company and request.membership based on
    the X-Company header or the user's default membership.
    """

    # Paths that don't require a company context
    EXEMPT_PREFIXES = (
        '/api/auth/',
        '/api/companies/',
        '/admin/',
        '/static/',
        '/media/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.company = None
        request.membership = None

        # Skip for anonymous or exempt paths
        if not hasattr(request, 'user') or request.user.is_anonymous:
            return self.get_response(request)

        if any(request.path.startswith(p) for p in self.EXEMPT_PREFIXES):
            return self.get_response(request)

        # Resolve company
        company_id = request.headers.get('X-Company')

        if company_id:
            # Explicit company from header
            try:
                membership = Membership.objects.select_related('company').get(
                    user=request.user,
                    company_id=int(company_id),
                )
            except (Membership.DoesNotExist, ValueError):
                return JsonResponse(
                    {'detail': 'No tienes acceso a esta empresa.'},
                    status=403,
                )
        else:
            # Fallback to default company
            membership = Membership.objects.select_related('company').filter(
                user=request.user,
                is_default=True,
            ).first()

            if not membership:
                # Use first available
                membership = Membership.objects.select_related('company').filter(
                    user=request.user,
                ).first()

        if membership:
            request.company = membership.company
            request.membership = membership

        return self.get_response(request)
