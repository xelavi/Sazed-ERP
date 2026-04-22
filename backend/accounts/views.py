"""
Views for accounts app — auth, profile, companies, members.
"""

from django.contrib.auth import login, logout
from django.utils.text import slugify
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from .models import User, Company, Membership
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    CompanySerializer,
    CompanyCreateSerializer,
    MembershipSerializer,
    InviteMemberSerializer,
    SwitchCompanySerializer,
)


# ── Auth endpoints ─────────────────────────────────────


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ — Create account (company is optional)."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)

        # Return user + their default company (if any)
        membership = user.memberships.select_related('company').first()
        response_data = {
            'user': UserSerializer(user).data,
            'company': None,
            'role': None,
        }
        if membership:
            response_data['company'] = CompanySerializer(membership.company).data
            response_data['role'] = membership.role

        return Response(response_data, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """POST /api/auth/login/ — Session login."""

    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)

        # Get default (or first) company
        membership = user.memberships.select_related('company').filter(
            is_default=True,
        ).first() or user.memberships.select_related('company').first()

        company_data = None
        role = None
        if membership:
            company_data = CompanySerializer(membership.company).data
            role = membership.role

        return Response({
            'user': UserSerializer(user).data,
            'company': company_data,
            'role': role,
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """POST /api/auth/logout/ — Session logout."""
    logout(request)
    return Response({'detail': 'Sesión cerrada.'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def me_view(request):
    """GET /api/auth/me/ — Current user + companies."""
    user = request.user
    memberships = user.memberships.select_related('company').all()

    companies = []
    for m in memberships:
        companies.append({
            'id': m.company.id,
            'name': m.company.name,
            'slug': m.company.slug,
            'logo': m.company.logo.url if m.company.logo else None,
            'role': m.role,
            'is_default': m.is_default,
        })

    return Response({
        'user': UserSerializer(user).data,
        'companies': companies,
    })


# ── Profile ────────────────────────────────────────────


class ProfileUpdateView(generics.UpdateAPIView):
    """PATCH /api/auth/profile/ — Update own profile."""

    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.GenericAPIView):
    """POST /api/auth/change-password/"""

    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        login(request, request.user)  # Keep session alive
        return Response({'detail': 'Contraseña actualizada.'})


# ── Companies ──────────────────────────────────────────


class CompanyViewSet(viewsets.ModelViewSet):
    """CRUD for companies the user belongs to."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CompanyCreateSerializer
        return CompanySerializer

    def get_queryset(self):
        return Company.objects.filter(
            memberships__user=self.request.user,
        ).distinct()

    @action(detail=False, methods=['post'], url_path='switch')
    def switch(self, request):
        """POST /api/companies/switch/ — Switch active company."""
        serializer = SwitchCompanySerializer(
            data=request.data, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        company_id = serializer.validated_data['company_id']

        # Set new default
        Membership.objects.filter(user=request.user, is_default=True).update(
            is_default=False,
        )
        membership = Membership.objects.get(
            user=request.user, company_id=company_id,
        )
        membership.is_default = True
        membership.save(update_fields=['is_default'])

        return Response({
            'company': CompanySerializer(membership.company).data,
            'role': membership.role,
        })

    @action(detail=True, methods=['get', 'post'], url_path='members')
    def members(self, request, pk=None):
        """GET/POST /api/companies/{id}/members/"""
        company = self.get_object()

        # Check permission
        user_membership = Membership.objects.get(
            user=request.user, company=company,
        )

        if request.method == 'GET':
            memberships = company.memberships.select_related('user').all()
            serializer = MembershipSerializer(memberships, many=True)
            return Response(serializer.data)

        # POST — invite member
        if not user_membership.can_manage:
            return Response(
                {'detail': 'No tienes permiso para invitar miembros.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = InviteMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        role = serializer.validated_data['role']

        # Find or note that user doesn't exist yet
        try:
            invite_user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'detail': f'No hay ninguna cuenta registrada con {email}.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if already a member
        if Membership.objects.filter(user=invite_user, company=company).exists():
            return Response(
                {'detail': 'El usuario ya es miembro de esta empresa.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        membership = Membership.objects.create(
            user=invite_user,
            company=company,
            role=role,
            invited_by=request.user,
        )

        return Response(
            MembershipSerializer(membership).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True, methods=['patch', 'delete'],
        url_path='members/(?P<member_id>[0-9]+)',
    )
    def manage_member(self, request, pk=None, member_id=None):
        """
        PATCH /api/companies/{id}/members/{member_id}/ — Change role
        DELETE /api/companies/{id}/members/{member_id}/ — Remove member
        """
        company = self.get_object()
        user_membership = Membership.objects.get(
            user=request.user, company=company,
        )

        if not user_membership.can_manage:
            return Response(
                {'detail': 'No tienes permiso para gestionar miembros.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            target = Membership.objects.get(id=member_id, company=company)
        except Membership.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Can't modify the sole owner
        if target.is_owner and request.method == 'DELETE':
            return Response(
                {'detail': 'No puedes eliminar al propietario.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == 'DELETE':
            target.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        # PATCH — update role
        new_role = request.data.get('role')
        if new_role and new_role in dict(Membership.Role.choices):
            target.role = new_role
            target.save(update_fields=['role'])

        return Response(MembershipSerializer(target).data)
