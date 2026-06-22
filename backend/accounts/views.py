"""
Views for accounts app — auth, profile, companies, members.
"""

import secrets
import urllib.parse

from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.text import slugify
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Q
from django.utils import timezone

from .models import (
    User, Company, Membership, Role, Notification, Message, Invitation,
    SocialAccount, SocialPost, SystemSettings, MODULES,
)
from .services import facebook as fb_service
from .services import youtube as yt_service
from .services import twitter as tw_service
from .services import tiktok as tt_service
from rest_framework.exceptions import PermissionDenied
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    UserLiteSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    CompanySerializer,
    CompanyCreateSerializer,
    MembershipSerializer,
    RoleSerializer,
    InviteMemberSerializer,
    SwitchCompanySerializer,
    NotificationSerializer,
    MessageSerializer,
    MessageCreateSerializer,
    InvitationSerializer,
    InvitationCreateSerializer,
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
            'role_label': None,
            'permissions': None,
        }
        if membership:
            response_data['company'] = CompanySerializer(membership.company).data
            response_data['role'] = membership.role
            response_data['role_label'] = membership.role_label
            response_data['permissions'] = membership.effective_permissions

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
        role_label = None
        perms = None
        if membership:
            company_data = CompanySerializer(membership.company).data
            role = membership.role
            role_label = membership.role_label
            perms = membership.effective_permissions

        return Response({
            'user': UserSerializer(user).data,
            'company': company_data,
            'role': role,
            'role_label': role_label,
            'permissions': perms,
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
            'role_label': m.role_label,
            'permissions': m.effective_permissions,
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

    def destroy(self, request, *args, **kwargs):
        company = self.get_object()
        try:
            membership = Membership.objects.get(
                user=request.user, company=company,
            )
        except Membership.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not membership.is_owner:
            return Response(
                {'detail': 'Solo el propietario puede eliminar la empresa.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        company.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
            'role_label': membership.role_label,
            'permissions': membership.effective_permissions,
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
        custom_role_id = serializer.validated_data.get('custom_role')

        # Resolve an optional custom role (must belong to this company).
        custom_role = None
        if custom_role_id:
            try:
                custom_role = Role.objects.get(id=custom_role_id, company=company)
            except Role.DoesNotExist:
                return Response(
                    {'detail': 'Rol no válido para esta empresa.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # A custom role implies a non-privileged base role.
            role = 'editor'

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
            custom_role=custom_role,
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

        # Protect the owner's role from being changed.
        if target.is_owner and (
            'role' in request.data or 'custom_role' in request.data
        ):
            return Response(
                {'detail': 'No puedes cambiar el rol del propietario.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        membership_updates = []

        # PATCH — update builtin role
        new_role = request.data.get('role')
        if new_role and new_role in dict(Membership.Role.choices):
            target.role = new_role
            membership_updates.append('role')
            # A builtin role and a custom role are mutually exclusive.
            if target.custom_role_id:
                target.custom_role = None
                membership_updates.append('custom_role')

        # PATCH — assign or clear a custom role
        if 'custom_role' in request.data:
            custom_role_id = request.data.get('custom_role')
            if custom_role_id in (None, '', 0):
                target.custom_role = None
            else:
                try:
                    role_obj = Role.objects.get(id=custom_role_id, company=company)
                except (Role.DoesNotExist, ValueError, TypeError):
                    return Response(
                        {'detail': 'Rol no válido para esta empresa.'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                target.custom_role = role_obj
                # A custom role implies a non-privileged base role.
                if target.role in ('owner', 'admin'):
                    target.role = 'editor'
                    if 'role' not in membership_updates:
                        membership_updates.append('role')
            membership_updates.append('custom_role')

        if membership_updates:
            target.save(update_fields=list(set(membership_updates)))

        # Allow admins to edit user fields of the member
        user_fields = ['first_name', 'last_name']
        user_updates = {f: request.data[f] for f in user_fields if f in request.data}
        if user_updates:
            for k, v in user_updates.items():
                setattr(target.user, k, v)
            target.user.save(update_fields=list(user_updates.keys()))

        return Response(MembershipSerializer(target).data)

    # ── Roles (custom, per-company) ──

    @action(detail=True, methods=['get', 'post'], url_path='roles')
    def roles(self, request, pk=None):
        """
        GET  /api/companies/{id}/roles/ — List custom roles (any member)
        POST /api/companies/{id}/roles/ — Create a role (managers only)
        """
        company = self.get_object()
        user_membership = Membership.objects.get(
            user=request.user, company=company,
        )

        if request.method == 'GET':
            serializer = RoleSerializer(company.roles.all(), many=True)
            return Response({
                'roles': serializer.data,
                'modules': [{'key': k, 'label': l} for k, l in MODULES],
            })

        if not user_membership.can_manage:
            return Response(
                {'detail': 'No tienes permiso para gestionar roles.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = RoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if company.roles.filter(name__iexact=serializer.validated_data['name']).exists():
            return Response(
                {'detail': 'Ya existe un rol con ese nombre.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save(company=company)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True, methods=['patch', 'delete'],
        url_path='roles/(?P<role_id>[0-9]+)',
    )
    def manage_role(self, request, pk=None, role_id=None):
        """
        PATCH  /api/companies/{id}/roles/{role_id}/ — Update a role
        DELETE /api/companies/{id}/roles/{role_id}/ — Delete a role
        """
        company = self.get_object()
        user_membership = Membership.objects.get(
            user=request.user, company=company,
        )
        if not user_membership.can_manage:
            return Response(
                {'detail': 'No tienes permiso para gestionar roles.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            role_obj = Role.objects.get(id=role_id, company=company)
        except Role.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'DELETE':
            # Members keep their builtin role; custom_role is cleared by SET_NULL.
            role_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = RoleSerializer(role_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        new_name = serializer.validated_data.get('name')
        if new_name and company.roles.filter(
            name__iexact=new_name,
        ).exclude(id=role_obj.id).exists():
            return Response(
                {'detail': 'Ya existe un rol con ese nombre.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response(serializer.data)


# ── User search (within active company) ───────────────


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_search(request):
    """GET /api/users/search/?q=... — Find users in the active company."""
    company_id = request.headers.get('X-Company') or request.META.get('HTTP_X_COMPANY')
    if not company_id:
        return Response([], status=200)

    if not Membership.objects.filter(
        user=request.user, company_id=company_id,
    ).exists():
        return Response(
            {'detail': 'No perteneces a esta empresa.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    q = (request.query_params.get('q') or '').strip()
    qs = User.objects.filter(memberships__company_id=company_id).exclude(
        id=request.user.id,
    ).distinct()
    if q:
        qs = qs.filter(
            Q(email__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q),
        )
    return Response(UserLiteSerializer(qs[:10], many=True).data)


# ── Inbox: summary ─────────────────────────────────────


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def inbox_summary(request):
    """GET /api/inbox/summary/ — Unread counts for badge."""
    user = request.user
    notifications = Notification.objects.filter(recipient=user, read=False).count()
    messages = Message.objects.filter(recipient=user, read=False).count()
    invitations = Invitation.objects.filter(invitee=user, status='pending').count()
    return Response({
        'notifications': notifications,
        'messages': messages,
        'invitations': invitations,
        'total': notifications + messages + invitations,
    })


# ── Notifications ──────────────────────────────────────


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """List own notifications + mark-read actions."""

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=True, methods=['post'], url_path='read')
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        if not notif.read:
            notif.read = True
            notif.save(update_fields=['read'])
        return Response(NotificationSerializer(notif).data)

    @action(detail=False, methods=['post'], url_path='read-all')
    def mark_all_read(self, request):
        self.get_queryset().filter(read=False).update(read=True)
        return Response({'detail': 'OK'})


# ── Messages ───────────────────────────────────────────


class MessageViewSet(viewsets.ModelViewSet):
    """User-to-user messages within the active company."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def get_queryset(self):
        user = self.request.user
        # Messages where user is sender or recipient
        return Message.objects.filter(
            Q(recipient=user) | Q(sender=user),
        ).select_related('sender', 'recipient', 'company')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        return Response(
            MessageSerializer(message).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'], url_path='read')
    def mark_read(self, request, pk=None):
        message = self.get_object()
        if message.recipient_id == request.user.id and not message.read:
            message.read = True
            message.save(update_fields=['read'])
        return Response(MessageSerializer(message).data)

    @action(detail=False, methods=['post'], url_path='read-all')
    def mark_all_read(self, request):
        Message.objects.filter(recipient=request.user, read=False).update(read=True)
        return Response({'detail': 'OK'})


# ── Invitations ────────────────────────────────────────


class InvitationViewSet(viewsets.ModelViewSet):
    """
    List invitations sent/received by the current user.
    POST = create invitation (admin/owner of company).
    Accept/reject actions for the invitee.
    """

    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        return Invitation.objects.filter(
            Q(invitee=user) | Q(inviter=user),
        ).select_related('company', 'inviter', 'invitee')

    def create(self, request, *args, **kwargs):
        company_id = (
            request.headers.get('X-Company')
            or request.META.get('HTTP_X_COMPANY')
        )
        if not company_id:
            return Response(
                {'detail': 'Falta el contexto de empresa.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            membership = Membership.objects.get(
                user=request.user, company_id=company_id,
            )
        except Membership.DoesNotExist:
            return Response(
                {'detail': 'No perteneces a esta empresa.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not membership.can_manage:
            return Response(
                {'detail': 'No tienes permiso para invitar miembros.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = InvitationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        role = serializer.validated_data['role']
        custom_role_id = serializer.validated_data.get('custom_role')

        # Resolve an optional custom role (must belong to this company).
        custom_role = None
        if custom_role_id:
            try:
                custom_role = Role.objects.get(id=custom_role_id, company_id=company_id)
            except Role.DoesNotExist:
                return Response(
                    {'detail': 'Rol no válido para esta empresa.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            role = 'editor'

        try:
            invitee = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'detail': f'No hay ninguna cuenta registrada con {email}.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if invitee.id == request.user.id:
            return Response(
                {'detail': 'No puedes invitarte a ti mismo.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Membership.objects.filter(
            user=invitee, company_id=company_id,
        ).exists():
            return Response(
                {'detail': 'El usuario ya es miembro de esta empresa.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Invitation.objects.filter(
            company_id=company_id, invitee=invitee, status='pending',
        ).exists():
            return Response(
                {'detail': 'Ya hay una invitación pendiente para este usuario.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation = Invitation.objects.create(
            company_id=company_id,
            inviter=request.user,
            invitee=invitee,
            role=role,
            custom_role=custom_role,
        )
        return Response(
            InvitationSerializer(invitation).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, pk=None):
        invitation = self.get_object()
        if invitation.invitee_id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if invitation.status != 'pending':
            return Response(
                {'detail': 'Esta invitación ya ha sido respondida.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Avoid duplicates if user joined via another path meanwhile
        if not Membership.objects.filter(
            user=request.user, company=invitation.company,
        ).exists():
            Membership.objects.create(
                user=request.user,
                company=invitation.company,
                role=invitation.role,
                custom_role=invitation.custom_role,
                invited_by=invitation.inviter,
            )

        invitation.status = 'accepted'
        invitation.responded_at = timezone.now()
        invitation.save(update_fields=['status', 'responded_at'])
        return Response(InvitationSerializer(invitation).data)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        invitation = self.get_object()
        if invitation.invitee_id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if invitation.status != 'pending':
            return Response(
                {'detail': 'Esta invitación ya ha sido respondida.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        invitation.status = 'rejected'
        invitation.responded_at = timezone.now()
        invitation.save(update_fields=['status', 'responded_at'])
        return Response(InvitationSerializer(invitation).data)


# ── Permission helpers ─────────────────────────────────


def _can_manage_system_settings(user) -> bool:
    """
    True for Django staff OR company owners/admins.
    is_staff is the Django admin flag; owner/admin is the ERP company role.
    """
    if user.is_staff:
        return True
    return user.memberships.filter(role__in=['owner', 'admin']).exists()


# ── Facebook OAuth + Graph API ─────────────────────────


FACEBOOK_SCOPES = [
    'email',
    'public_profile',
    'pages_show_list',
    'pages_read_engagement',
    'pages_manage_metadata',
    'instagram_basic',
    'instagram_manage_insights',
    'business_management',
]


def _login_payload(user):
    """Same response shape as LoginView so the frontend reuses one handler."""
    membership = user.memberships.select_related('company').filter(
        is_default=True,
    ).first() or user.memberships.select_related('company').first()

    company_data = None
    role = None
    role_label = None
    perms = None
    if membership:
        company_data = CompanySerializer(membership.company).data
        role = membership.role
        role_label = membership.role_label
        perms = membership.effective_permissions

    return {
        'user': UserSerializer(user).data,
        'company': company_data,
        'role': role,
        'role_label': role_label,
        'permissions': perms,
    }


class FacebookLoginView(APIView):
    """
    POST /api/auth/facebook/
    Body: { "access_token": "<short-lived FB token from JS SDK>" }

    Verifies the token, exchanges it for a long-lived one, finds or
    creates a User by email, links it via SocialAccount, opens a Django
    session, and returns the same payload as the email/password login.
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # avoid CSRF (no session yet)

    def post(self, request):
        short_token = (request.data or {}).get('access_token')
        if not short_token:
            return Response(
                {'detail': 'Falta el access_token de Facebook.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            debug = fb_service.debug_token(short_token)
            exchanged = fb_service.exchange_for_long_lived(short_token)
            long_token = exchanged.get('access_token') or short_token
            expires_at = fb_service.expires_at_from(exchanged.get('expires_in'))
            me = fb_service.get_me(long_token)
        except fb_service.FacebookAPIError as exc:
            code = exc.status_code if exc.status_code in (400, 401, 403, 502) else 400
            return Response({'detail': str(exc)}, status=code)

        fb_id = me.get('id')
        email = (me.get('email') or '').lower().strip()
        if not fb_id:
            return Response(
                {'detail': 'Respuesta de Facebook sin id de usuario.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not email:
            return Response(
                {'detail': (
                    'Tu cuenta de Facebook no expone email. '
                    'Concede el permiso "email" e inténtalo de nuevo.'
                )},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Find or link by email; create if missing.
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': me.get('first_name') or me.get('name') or 'Usuario',
                'last_name': me.get('last_name') or '',
            },
        )
        if created:
            user.set_unusable_password()
            user.save(update_fields=['password'])

        SocialAccount.objects.update_or_create(
            provider=SocialAccount.PROVIDER_FACEBOOK,
            provider_user_id=str(fb_id),
            defaults={
                'user': user,
                'access_token': long_token,
                'token_expires_at': expires_at,
                'scopes': debug.get('scopes', []),
                'extra_data': {
                    'name': me.get('name', ''),
                    'picture': (me.get('picture') or {}).get('data', {}).get('url', ''),
                },
            },
        )

        login(request, user)
        return Response(_login_payload(user))


def _get_fb_account(user):
    return SocialAccount.objects.filter(
        user=user, provider=SocialAccount.PROVIDER_FACEBOOK,
    ).first()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def facebook_pages(request):
    """GET /api/integrations/facebook/pages/ — Pages the user manages."""
    account = _get_fb_account(request.user)
    if not account:
        return Response(
            {'detail': 'No has conectado Facebook.'},
            status=status.HTTP_404_NOT_FOUND,
        )
    try:
        pages = fb_service.list_pages(account.access_token)
    except fb_service.FacebookAPIError as exc:
        return Response({'detail': str(exc)}, status=exc.status_code or 400)

    # Hide page tokens — they're meant for server use only.
    sanitized = [
        {k: v for k, v in p.items() if k != 'access_token'}
        for p in pages
    ]
    return Response({'pages': sanitized})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def facebook_instagram(request):
    """
    GET /api/integrations/facebook/instagram/?page_id=<id>
    Returns the Instagram Business account linked to that Page (if any).
    """
    page_id = request.query_params.get('page_id')
    if not page_id:
        return Response(
            {'detail': 'Falta el parámetro page_id.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    account = _get_fb_account(request.user)
    if not account:
        return Response(
            {'detail': 'No has conectado Facebook.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        pages = fb_service.list_pages(account.access_token)
        match = next((p for p in pages if str(p.get('id')) == str(page_id)), None)
        if not match:
            return Response(
                {'detail': 'No tienes acceso a esa página.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        ig = fb_service.get_instagram_for_page(page_id, match['access_token'])
    except fb_service.FacebookAPIError as exc:
        return Response({'detail': str(exc)}, status=exc.status_code or 400)

    return Response({'instagram': ig})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def facebook_disconnect(request):
    """POST /api/integrations/facebook/disconnect/ — Forget stored FB token."""
    deleted, _ = SocialAccount.objects.filter(
        user=request.user, provider=SocialAccount.PROVIDER_FACEBOOK,
    ).delete()
    return Response({'detail': 'Facebook desconectado.', 'deleted': deleted})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def facebook_connect(request):
    """
    POST /api/integrations/facebook/connect/
    Body: { "access_token": "<short-lived FB token from JS SDK>" }

    Links a Facebook account to the currently authenticated user.
    Does NOT create a new session — the user is already logged in.
    """
    short_token = (request.data or {}).get('access_token')
    if not short_token:
        return Response(
            {'detail': 'Falta el access_token de Facebook.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        debug = fb_service.debug_token(short_token)
        exchanged = fb_service.exchange_for_long_lived(short_token)
        long_token = exchanged.get('access_token') or short_token
        expires_at = fb_service.expires_at_from(exchanged.get('expires_in'))
        me = fb_service.get_me(long_token)
    except fb_service.FacebookAPIError as exc:
        code = exc.status_code if exc.status_code in (400, 401, 403, 502) else 400
        return Response({'detail': str(exc)}, status=code)

    fb_id = me.get('id')
    if not fb_id:
        return Response(
            {'detail': 'Respuesta de Facebook sin id de usuario.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check this FB account isn't already linked to a different user
    existing = SocialAccount.objects.filter(
        provider=SocialAccount.PROVIDER_FACEBOOK,
        provider_user_id=str(fb_id),
    ).exclude(user=request.user).first()
    if existing:
        return Response(
            {'detail': 'Esta cuenta de Facebook ya está vinculada a otro usuario.'},
            status=status.HTTP_409_CONFLICT,
        )

    SocialAccount.objects.update_or_create(
        provider=SocialAccount.PROVIDER_FACEBOOK,
        provider_user_id=str(fb_id),
        defaults={
            'user': request.user,
            'access_token': long_token,
            'token_expires_at': expires_at,
            'scopes': debug.get('scopes', []),
            'extra_data': {
                'name': me.get('name', ''),
                'picture': (me.get('picture') or {}).get('data', {}).get('url', ''),
            },
        },
    )

    return Response({
        'detail': 'Facebook vinculado correctamente.',
        'provider_user_id': str(fb_id),
        'name': me.get('name', ''),
        'picture': (me.get('picture') or {}).get('data', {}).get('url', ''),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def facebook_status(request):
    """GET /api/integrations/facebook/status/ — Is FB connected for current user?"""
    account = _get_fb_account(request.user)
    if not account:
        return Response({'connected': False})
    return Response({
        'connected': True,
        'provider_user_id': account.provider_user_id,
        'token_expires_at': account.token_expires_at,
        'scopes': account.scopes,
        'extra_data': account.extra_data,
    })


# ── System Settings API (admin-only) ────────────────────


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def facebook_app_config(request):
    """
    GET /api/settings/facebook/app-id/ — Public: returns only the App ID.
    The App ID is not a secret (it's embedded in every webpage that uses FB Login).
    Used by the frontend to initialise the Facebook JS SDK without hardcoding .env.
    """
    app_id = fb_service._get_app_id()
    return Response({
        'facebook_app_id': app_id or '',
        'configured': bool(app_id),
    })


@api_view(['GET', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def system_settings_facebook(request):
    """
    GET /api/settings/facebook/ — Read current FB settings (staff only)
    PATCH /api/settings/facebook/ — Update FB settings (staff only)
    """
    if not _can_manage_system_settings(request.user):
        raise PermissionDenied('Solo propietarios y administradores pueden acceder a configuración del sistema.')

    if request.method == 'GET':
        secret = SystemSettings.get('facebook_app_secret') or ''
        return Response({
            'facebook_app_id': SystemSettings.get('facebook_app_id', ''),
            'facebook_app_secret_set': bool(secret),
            'facebook_graph_version': SystemSettings.get('facebook_graph_version', 'v19.0'),
        })

    # PATCH
    data = request.data or {}
    if 'facebook_app_id' in data:
        SystemSettings.set('facebook_app_id', (data['facebook_app_id'] or '').strip())
    if 'facebook_app_secret' in data:
        SystemSettings.set('facebook_app_secret', (data['facebook_app_secret'] or '').strip())
    if 'facebook_graph_version' in data:
        SystemSettings.set('facebook_graph_version', data['facebook_graph_version'])

    return Response({
        'detail': 'Configuración guardada. Los cambios se aplican inmediatamente.',
        'facebook_app_id': SystemSettings.get('facebook_app_id', ''),
        'facebook_app_secret_set': bool(SystemSettings.get('facebook_app_secret')),
    })


# ── YouTube (Google Identity Services) ─────────────────
# Token flow: GIS initTokenClient (popup) returns access_token directly.
# Frontend sends it here; we validate via Google tokeninfo and store.


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def youtube_connect(request):
    """
    POST /api/integrations/youtube/connect/
    Body: { "access_token": "<token from GIS initTokenClient>" }
    """
    access_token = (request.data or {}).get('access_token')
    if not access_token:
        return Response({'detail': 'Falta el access_token de Google.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        token_info = yt_service.validate_token(access_token)
        user_info = yt_service.get_userinfo(access_token)
    except yt_service.YouTubeAPIError as exc:
        code = exc.status_code if exc.status_code in (400, 401, 403, 502) else 400
        return Response({'detail': str(exc)}, status=code)

    google_id = token_info.get('sub') or user_info.get('sub')
    if not google_id:
        return Response({'detail': 'No se pudo obtener el id de Google.'}, status=status.HTTP_400_BAD_REQUEST)

    SocialAccount.objects.filter(
        provider=SocialAccount.PROVIDER_YOUTUBE,
        provider_user_id=str(google_id),
    ).exclude(user=request.user).delete()

    expires_at = yt_service.expires_at_from(token_info.get('exp') and (int(token_info['exp']) - int(timezone.now().timestamp())))

    SocialAccount.objects.update_or_create(
        provider=SocialAccount.PROVIDER_YOUTUBE,
        provider_user_id=str(google_id),
        defaults={
            'user': request.user,
            'access_token': access_token,
            'token_expires_at': expires_at,
            'scopes': token_info.get('scope', '').split() if token_info.get('scope') else [],
            'extra_data': {
                'name': user_info.get('name', ''),
                'email': user_info.get('email', ''),
                'picture': user_info.get('picture', ''),
            },
        },
    )

    return Response({
        'detail': 'YouTube vinculado correctamente.',
        'provider_user_id': str(google_id),
        'name': user_info.get('name', ''),
        'picture': user_info.get('picture', ''),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def youtube_status(request):
    """GET /api/integrations/youtube/status/"""
    account = SocialAccount.objects.filter(
        user=request.user, provider=SocialAccount.PROVIDER_YOUTUBE,
    ).first()
    if not account:
        return Response({'connected': False})
    return Response({
        'connected': True,
        'provider_user_id': account.provider_user_id,
        'token_expires_at': account.token_expires_at,
        'scopes': account.scopes,
        'extra_data': account.extra_data,
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def youtube_disconnect(request):
    """POST /api/integrations/youtube/disconnect/"""
    deleted, _ = SocialAccount.objects.filter(
        user=request.user, provider=SocialAccount.PROVIDER_YOUTUBE,
    ).delete()
    return Response({'detail': 'YouTube desconectado.', 'deleted': deleted})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def youtube_channels(request):
    """GET /api/integrations/youtube/channels/ — Channel statistics."""
    account = SocialAccount.objects.filter(
        user=request.user, provider=SocialAccount.PROVIDER_YOUTUBE,
    ).first()
    if not account:
        return Response({'detail': 'No has conectado YouTube.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        channels = yt_service.get_channels(account.access_token)
    except yt_service.YouTubeAPIError as exc:
        return Response({'detail': str(exc)}, status=exc.status_code or 400)

    return Response({'channels': channels})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def youtube_app_config(request):
    """GET /api/settings/youtube/client-id/ — Public: Client ID for GIS init."""
    client_id = yt_service._get_client_id()
    return Response({'youtube_client_id': client_id or '', 'configured': bool(client_id)})


@api_view(['GET', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def system_settings_youtube(request):
    """GET/PATCH /api/settings/youtube/ — Staff only."""
    if not _can_manage_system_settings(request.user):
        raise PermissionDenied('Solo propietarios y administradores pueden acceder a configuración del sistema.')

    if request.method == 'GET':
        return Response({
            'youtube_client_id': SystemSettings.get('youtube_client_id', ''),
            'youtube_client_secret_set': bool(SystemSettings.get('youtube_client_secret')),
        })

    data = request.data or {}
    if 'youtube_client_id' in data:
        SystemSettings.set('youtube_client_id', (data['youtube_client_id'] or '').strip())
    if 'youtube_client_secret' in data:
        SystemSettings.set('youtube_client_secret', (data['youtube_client_secret'] or '').strip())

    return Response({
        'detail': 'Configuración guardada.',
        'youtube_client_id': SystemSettings.get('youtube_client_id', ''),
        'youtube_client_secret_set': bool(SystemSettings.get('youtube_client_secret')),
    })


# ── X (Twitter) OAuth 2.0 PKCE ─────────────────────────
# Popup flow: browser opens /api/integrations/twitter/init/ →
# backend redirects to Twitter → Twitter redirects to /callback/ →
# backend stores token, redirects popup to /oauth/done on frontend.


@csrf_exempt
def twitter_init(request):
    """GET /api/integrations/twitter/init/ — Starts OAuth 2.0 PKCE popup flow."""
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
    done_url = f'{frontend_url}/oauth/done'

    client_id = tw_service._get_client_id()
    if not client_id:
        return HttpResponseRedirect(f'{done_url}?platform=twitter&error={urllib.parse.quote("X no está configurado.")}')

    code_verifier = tw_service.generate_code_verifier()
    code_challenge = tw_service.generate_code_challenge(code_verifier)
    state = secrets.token_urlsafe(32)

    request.session['twitter_oauth_state'] = state
    request.session['twitter_oauth_verifier'] = code_verifier

    backend_base = f'{request.scheme}://{request.get_host()}'
    redirect_uri = f'{backend_base}/api/integrations/twitter/callback/'

    try:
        auth_url = tw_service.build_auth_url(redirect_uri, state, code_challenge)
    except tw_service.TwitterAPIError as exc:
        return HttpResponseRedirect(f'{done_url}?platform=twitter&error={urllib.parse.quote(str(exc))}')

    return HttpResponseRedirect(auth_url)


def twitter_callback(request):
    """GET /api/integrations/twitter/callback/ — Twitter redirects here after auth."""
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
    done_url = f'{frontend_url}/oauth/done'

    error = request.GET.get('error')
    if error:
        return HttpResponseRedirect(
            f'{done_url}?platform=twitter&error={urllib.parse.quote(request.GET.get("error_description", error))}',
        )

    code = request.GET.get('code')
    state = request.GET.get('state')
    session_state = request.session.pop('twitter_oauth_state', None)
    code_verifier = request.session.pop('twitter_oauth_verifier', None)

    if not state or state != session_state:
        return HttpResponseRedirect(
            f'{done_url}?platform=twitter&error={urllib.parse.quote("Estado OAuth inválido.")}',
        )
    if not code or not code_verifier:
        return HttpResponseRedirect(
            f'{done_url}?platform=twitter&error={urllib.parse.quote("Código de autorización no recibido.")}',
        )
    if not request.user.is_authenticated:
        return HttpResponseRedirect(
            f'{done_url}?platform=twitter&error={urllib.parse.quote("Sesión expirada. Inicia sesión de nuevo.")}',
        )

    backend_base = f'{request.scheme}://{request.get_host()}'
    redirect_uri = f'{backend_base}/api/integrations/twitter/callback/'

    try:
        tokens = tw_service.exchange_code(code, code_verifier, redirect_uri)
        access_token = tokens['access_token']
        me = tw_service.get_me(access_token)
    except tw_service.TwitterAPIError as exc:
        return HttpResponseRedirect(f'{done_url}?platform=twitter&error={urllib.parse.quote(str(exc))}')

    twitter_id = me.get('id')
    if not twitter_id:
        return HttpResponseRedirect(
            f'{done_url}?platform=twitter&error={urllib.parse.quote("No se pudo obtener el id de X.")}',
        )

    SocialAccount.objects.update_or_create(
        provider=SocialAccount.PROVIDER_TWITTER,
        provider_user_id=str(twitter_id),
        defaults={
            'user': request.user,
            'access_token': access_token,
            'token_expires_at': tw_service.expires_at_from(tokens.get('expires_in')),
            'scopes': tokens.get('scope', '').split() if tokens.get('scope') else [],
            'extra_data': {
                'name': me.get('name', ''),
                'username': me.get('username', ''),
                'profile_image_url': me.get('profile_image_url', ''),
                'public_metrics': me.get('public_metrics', {}),
                'refresh_token': tokens.get('refresh_token', ''),
            },
        },
    )

    return HttpResponseRedirect(f'{done_url}?platform=twitter&success=1')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def twitter_status(request):
    """GET /api/integrations/twitter/status/"""
    account = SocialAccount.objects.filter(
        user=request.user, provider=SocialAccount.PROVIDER_TWITTER,
    ).first()
    if not account:
        return Response({'connected': False})
    return Response({
        'connected': True,
        'provider_user_id': account.provider_user_id,
        'token_expires_at': account.token_expires_at,
        'scopes': account.scopes,
        'extra_data': account.extra_data,
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def twitter_disconnect(request):
    """POST /api/integrations/twitter/disconnect/"""
    deleted, _ = SocialAccount.objects.filter(
        user=request.user, provider=SocialAccount.PROVIDER_TWITTER,
    ).delete()
    return Response({'detail': 'X desconectado.', 'deleted': deleted})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def twitter_metrics(request):
    """GET /api/integrations/twitter/metrics/ — User profile + recent tweet metrics."""
    account = SocialAccount.objects.filter(
        user=request.user, provider=SocialAccount.PROVIDER_TWITTER,
    ).first()
    if not account:
        return Response({'detail': 'No has conectado X.'}, status=status.HTTP_404_NOT_FOUND)

    access_token = account.access_token
    # Auto-refresh if expired
    if account.token_expires_at and account.token_expires_at <= timezone.now():
        refresh_token = account.extra_data.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'Token expirado. Reconecta X.'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            new_tokens = tw_service.refresh_access_token(refresh_token)
            access_token = new_tokens['access_token']
            account.access_token = access_token
            account.token_expires_at = tw_service.expires_at_from(new_tokens.get('expires_in'))
            if new_tokens.get('refresh_token'):
                account.extra_data['refresh_token'] = new_tokens['refresh_token']
            account.save(update_fields=['access_token', 'token_expires_at', 'extra_data'])
        except tw_service.TwitterAPIError as exc:
            return Response({'detail': str(exc)}, status=exc.status_code or 400)

    try:
        me = tw_service.get_me(access_token)
        tweets = tw_service.get_user_tweets(me['id'], access_token)
    except tw_service.TwitterAPIError as exc:
        return Response({'detail': str(exc)}, status=exc.status_code or 400)

    return Response({'user': me, 'tweets': tweets})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def twitter_app_config(request):
    """GET /api/settings/twitter/client-id/ — Public: returns Client ID."""
    client_id = tw_service._get_client_id()
    return Response({'twitter_client_id': client_id or '', 'configured': bool(client_id)})


@api_view(['GET', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def system_settings_twitter(request):
    """GET/PATCH /api/settings/twitter/ — Staff only."""
    if not _can_manage_system_settings(request.user):
        raise PermissionDenied('Solo propietarios y administradores pueden acceder a configuración del sistema.')

    if request.method == 'GET':
        return Response({
            'twitter_client_id': SystemSettings.get('twitter_client_id', ''),
            'twitter_client_secret_set': bool(SystemSettings.get('twitter_client_secret')),
        })

    data = request.data or {}
    if 'twitter_client_id' in data:
        SystemSettings.set('twitter_client_id', (data['twitter_client_id'] or '').strip())
    if 'twitter_client_secret' in data:
        SystemSettings.set('twitter_client_secret', (data['twitter_client_secret'] or '').strip())

    return Response({
        'detail': 'Configuración guardada.',
        'twitter_client_id': SystemSettings.get('twitter_client_id', ''),
        'twitter_client_secret_set': bool(SystemSettings.get('twitter_client_secret')),
    })


# ── TikTok OAuth 2.0 ───────────────────────────────────


@csrf_exempt
def tiktok_init(request):
    """GET /api/integrations/tiktok/init/ — Starts OAuth 2.0 popup flow."""
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
    done_url = f'{frontend_url}/oauth/done'

    client_key = tt_service._get_client_key()
    if not client_key:
        return HttpResponseRedirect(
            f'{done_url}?platform=tiktok&error={urllib.parse.quote("TikTok no está configurado.")}',
        )

    state = tt_service.generate_state()
    request.session['tiktok_oauth_state'] = state

    backend_base = f'{request.scheme}://{request.get_host()}'
    redirect_uri = f'{backend_base}/api/integrations/tiktok/callback/'

    try:
        auth_url = tt_service.build_auth_url(redirect_uri, state)
    except tt_service.TikTokAPIError as exc:
        return HttpResponseRedirect(f'{done_url}?platform=tiktok&error={urllib.parse.quote(str(exc))}')

    return HttpResponseRedirect(auth_url)


def tiktok_callback(request):
    """GET /api/integrations/tiktok/callback/ — TikTok redirects here after auth."""
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
    done_url = f'{frontend_url}/oauth/done'

    error = request.GET.get('error')
    if error:
        return HttpResponseRedirect(
            f'{done_url}?platform=tiktok&error={urllib.parse.quote(request.GET.get("error_description", error))}',
        )

    code = request.GET.get('code')
    state = request.GET.get('state')
    session_state = request.session.pop('tiktok_oauth_state', None)

    if not state or state != session_state:
        return HttpResponseRedirect(
            f'{done_url}?platform=tiktok&error={urllib.parse.quote("Estado OAuth inválido.")}',
        )
    if not code:
        return HttpResponseRedirect(
            f'{done_url}?platform=tiktok&error={urllib.parse.quote("Código de autorización no recibido.")}',
        )
    if not request.user.is_authenticated:
        return HttpResponseRedirect(
            f'{done_url}?platform=tiktok&error={urllib.parse.quote("Sesión expirada. Inicia sesión de nuevo.")}',
        )

    backend_base = f'{request.scheme}://{request.get_host()}'
    redirect_uri = f'{backend_base}/api/integrations/tiktok/callback/'

    try:
        tokens = tt_service.exchange_code(code, redirect_uri)
        access_token = tokens.get('access_token')
        open_id = tokens.get('open_id', '')
        user_info = tt_service.get_user_info(access_token, open_id)
    except tt_service.TikTokAPIError as exc:
        return HttpResponseRedirect(f'{done_url}?platform=tiktok&error={urllib.parse.quote(str(exc))}')

    tiktok_id = user_info.get('open_id') or open_id
    if not tiktok_id:
        return HttpResponseRedirect(
            f'{done_url}?platform=tiktok&error={urllib.parse.quote("No se pudo obtener el id de TikTok.")}',
        )

    SocialAccount.objects.update_or_create(
        provider=SocialAccount.PROVIDER_TIKTOK,
        provider_user_id=str(tiktok_id),
        defaults={
            'user': request.user,
            'access_token': access_token,
            'token_expires_at': tt_service.expires_at_from(tokens.get('expires_in')),
            'scopes': tokens.get('scope', '').split(',') if tokens.get('scope') else [],
            'extra_data': {
                'display_name': user_info.get('display_name', ''),
                'avatar_url': user_info.get('avatar_url', ''),
                'follower_count': user_info.get('follower_count', 0),
                'video_count': user_info.get('video_count', 0),
                'union_id': user_info.get('union_id', ''),
                'refresh_token': tokens.get('refresh_token', ''),
            },
        },
    )

    return HttpResponseRedirect(f'{done_url}?platform=tiktok&success=1')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def tiktok_status(request):
    """GET /api/integrations/tiktok/status/"""
    account = SocialAccount.objects.filter(
        user=request.user, provider=SocialAccount.PROVIDER_TIKTOK,
    ).first()
    if not account:
        return Response({'connected': False})
    return Response({
        'connected': True,
        'provider_user_id': account.provider_user_id,
        'token_expires_at': account.token_expires_at,
        'scopes': account.scopes,
        'extra_data': account.extra_data,
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def tiktok_disconnect(request):
    """POST /api/integrations/tiktok/disconnect/"""
    deleted, _ = SocialAccount.objects.filter(
        user=request.user, provider=SocialAccount.PROVIDER_TIKTOK,
    ).delete()
    return Response({'detail': 'TikTok desconectado.', 'deleted': deleted})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def tiktok_metrics(request):
    """GET /api/integrations/tiktok/metrics/ — User profile + recent video metrics."""
    account = SocialAccount.objects.filter(
        user=request.user, provider=SocialAccount.PROVIDER_TIKTOK,
    ).first()
    if not account:
        return Response({'detail': 'No has conectado TikTok.'}, status=status.HTTP_404_NOT_FOUND)

    access_token = account.access_token
    if account.token_expires_at and account.token_expires_at <= timezone.now():
        refresh_token = account.extra_data.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'Token expirado. Reconecta TikTok.'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            new_tokens = tt_service.refresh_access_token(refresh_token)
            access_token = new_tokens.get('access_token')
            account.access_token = access_token
            account.token_expires_at = tt_service.expires_at_from(new_tokens.get('expires_in'))
            if new_tokens.get('refresh_token'):
                account.extra_data['refresh_token'] = new_tokens['refresh_token']
            account.save(update_fields=['access_token', 'token_expires_at', 'extra_data'])
        except tt_service.TikTokAPIError as exc:
            return Response({'detail': str(exc)}, status=exc.status_code or 400)

    try:
        user_info = tt_service.get_user_info(access_token)
        videos = tt_service.get_video_list(access_token)
    except tt_service.TikTokAPIError as exc:
        return Response({'detail': str(exc)}, status=exc.status_code or 400)

    return Response({'user': user_info, 'videos': videos})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def tiktok_app_config(request):
    """GET /api/settings/tiktok/client-key/ — Public: returns Client Key."""
    client_key = tt_service._get_client_key()
    return Response({'tiktok_client_key': client_key or '', 'configured': bool(client_key)})


@api_view(['GET', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def system_settings_tiktok(request):
    """GET/PATCH /api/settings/tiktok/ — Staff only."""
    if not _can_manage_system_settings(request.user):
        raise PermissionDenied('Solo propietarios y administradores pueden acceder a configuración del sistema.')

    if request.method == 'GET':
        return Response({
            'tiktok_client_key': SystemSettings.get('tiktok_client_key', ''),
            'tiktok_client_secret_set': bool(SystemSettings.get('tiktok_client_secret')),
        })

    data = request.data or {}
    if 'tiktok_client_key' in data:
        SystemSettings.set('tiktok_client_key', (data['tiktok_client_key'] or '').strip())
    if 'tiktok_client_secret' in data:
        SystemSettings.set('tiktok_client_secret', (data['tiktok_client_secret'] or '').strip())

    return Response({
        'detail': 'Configuración guardada.',
        'tiktok_client_key': SystemSettings.get('tiktok_client_key', ''),
        'tiktok_client_secret_set': bool(SystemSettings.get('tiktok_client_secret')),
    })


# ── Social accounts list + stats sync ──────────────────────────────────────────


def _fetch_fresh_stats(account) -> dict:
    """Fetch live stats from the platform API. Returns {} on any error."""
    try:
        if account.provider == SocialAccount.PROVIDER_YOUTUBE:
            channels = yt_service.get_channels(account.access_token)
            if not channels:
                return {}
            ch = channels[0]
            st = ch.get('statistics', {})
            sn = ch.get('snippet', {})
            thumbs = sn.get('thumbnails', {})
            thumb_url = (
                thumbs.get('medium') or thumbs.get('default') or {}
            ).get('url', '')
            return {
                'subscribers': int(st.get('subscriberCount', 0)),
                'views': int(st.get('viewCount', 0)),
                'videos': int(st.get('videoCount', 0)),
                'channel_name': sn.get('title', ''),
                'channel_thumbnail': thumb_url,
            }

        if account.provider == SocialAccount.PROVIDER_TWITTER:
            # Auto-refresh token if expired
            access_token = account.access_token
            if account.token_expires_at and account.token_expires_at <= timezone.now():
                refresh_token = account.extra_data.get('refresh_token')
                if refresh_token:
                    new_tokens = tw_service.refresh_access_token(refresh_token)
                    access_token = new_tokens['access_token']
                    account.access_token = access_token
                    account.token_expires_at = tw_service.expires_at_from(new_tokens.get('expires_in'))
                    if new_tokens.get('refresh_token'):
                        account.extra_data['refresh_token'] = new_tokens['refresh_token']
                    account.save(update_fields=['access_token', 'token_expires_at', 'extra_data'])
            me = tw_service.get_me(access_token)
            m = me.get('public_metrics', {})
            return {
                'followers': m.get('followers_count', 0),
                'following': m.get('following_count', 0),
                'tweets': m.get('tweet_count', 0),
            }

        if account.provider == SocialAccount.PROVIDER_TIKTOK:
            access_token = account.access_token
            if account.token_expires_at and account.token_expires_at <= timezone.now():
                refresh_token = account.extra_data.get('refresh_token')
                if refresh_token:
                    new_tokens = tt_service.refresh_access_token(refresh_token)
                    access_token = new_tokens.get('access_token')
                    account.access_token = access_token
                    account.token_expires_at = tt_service.expires_at_from(new_tokens.get('expires_in'))
                    if new_tokens.get('refresh_token'):
                        account.extra_data['refresh_token'] = new_tokens['refresh_token']
                    account.save(update_fields=['access_token', 'token_expires_at', 'extra_data'])
            user_info = tt_service.get_user_info(access_token)
            return {
                'followers': user_info.get('follower_count', 0),
                'likes': user_info.get('likes_count', 0),
                'videos': user_info.get('video_count', 0),
            }

        if account.provider == SocialAccount.PROVIDER_FACEBOOK:
            # Page stats require pages_manage_metadata; basic profile is in extra_data
            return {'name': account.extra_data.get('name', '')}

    except Exception:
        pass

    return {}


def _serialize_account(account) -> dict:
    """Normalize a SocialAccount into a flat dict for the frontend."""
    ed = account.extra_data or {}
    st = account.stats or {}

    name = {
        SocialAccount.PROVIDER_YOUTUBE: st.get('channel_name') or ed.get('name', ''),
        SocialAccount.PROVIDER_TWITTER: ed.get('name', ''),
        SocialAccount.PROVIDER_TIKTOK:  ed.get('display_name', ''),
        SocialAccount.PROVIDER_FACEBOOK: ed.get('name', ''),
    }.get(account.provider, '')

    avatar = {
        SocialAccount.PROVIDER_YOUTUBE:  st.get('channel_thumbnail') or ed.get('picture', ''),
        SocialAccount.PROVIDER_TWITTER:  ed.get('profile_image_url', ''),
        SocialAccount.PROVIDER_TIKTOK:   ed.get('avatar_url', ''),
        SocialAccount.PROVIDER_FACEBOOK: ed.get('picture', ''),
    }.get(account.provider, '')

    username = {
        SocialAccount.PROVIDER_TWITTER: f"@{ed.get('username', '')}" if ed.get('username') else '',
        SocialAccount.PROVIDER_TIKTOK:  ed.get('display_name', ''),
    }.get(account.provider, '')

    return {
        'id': account.id,
        'provider': account.provider,
        'provider_user_id': account.provider_user_id,
        'name': name,
        'username': username,
        'avatar': avatar,
        'stats': st,
        'stats_synced_at': account.stats_synced_at,
        'token_expires_at': account.token_expires_at,
    }


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def social_accounts_list(request):
    """GET /api/integrations/social/accounts/ — All connected social accounts with stored stats."""
    accounts = SocialAccount.objects.filter(user=request.user).order_by('provider')
    return Response({'accounts': [_serialize_account(a) for a in accounts]})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def sync_social_stats(request):
    """
    POST /api/integrations/social/sync/           → sync all platforms
    POST /api/integrations/social/sync/?provider=youtube → sync one platform
    """
    provider_filter = request.query_params.get('provider')
    qs = SocialAccount.objects.filter(user=request.user)
    if provider_filter:
        qs = qs.filter(provider=provider_filter)

    results = []
    for account in qs:
        fresh = _fetch_fresh_stats(account)
        if fresh:
            account.stats = fresh
            account.stats_synced_at = timezone.now()
            account.save(update_fields=['stats', 'stats_synced_at'])
            results.append({'provider': account.provider, 'ok': True, 'stats': fresh})
        else:
            results.append({'provider': account.provider, 'ok': False, 'stats': account.stats})

    accounts = SocialAccount.objects.filter(user=request.user).order_by('provider')
    return Response({
        'results': results,
        'accounts': [_serialize_account(a) for a in accounts],
    })


# ── Social posts (videos) ───────────────────────────────────────────────────


def _upsert_posts_for_account(account) -> list[dict]:
    """
    Fetch recent posts/videos from the platform API and upsert into SocialPost.
    Returns a list of serialized posts.
    """
    from dateutil import parser as dtparser

    saved = []

    try:
        if account.provider == SocialAccount.PROVIDER_YOUTUBE:
            channels = yt_service.get_channels(account.access_token)
            if not channels:
                return []
            channel_id = channels[0]['id']
            channel_name = channels[0].get('snippet', {}).get('title', '')
            videos = yt_service.get_recent_videos(account.access_token, channel_id, max_results=20)
            for v in videos:
                vid_id = v['id']
                snippet = v.get('snippet', {})
                stats   = v.get('statistics', {})
                thumbs  = snippet.get('thumbnails', {})
                thumb   = (thumbs.get('medium') or thumbs.get('high') or thumbs.get('default') or {}).get('url', '')
                pub_at  = None
                if snippet.get('publishedAt'):
                    try:
                        pub_at = dtparser.parse(snippet['publishedAt'])
                    except Exception:
                        pass
                post, _ = SocialPost.objects.update_or_create(
                    account=account,
                    platform_post_id=vid_id,
                    defaults={
                        'provider':      account.provider,
                        'title':         snippet.get('title', '')[:512],
                        'description':   snippet.get('description', '')[:2000],
                        'thumbnail_url': thumb,
                        'post_url':      f'https://www.youtube.com/watch?v={vid_id}',
                        'post_type':     SocialPost.POST_TYPE_VIDEO,
                        'published_at':  pub_at,
                        'views':         int(stats.get('viewCount', 0)),
                        'likes':         int(stats.get('likeCount', 0)),
                        'comments':      int(stats.get('commentCount', 0)),
                    },
                )
                saved.append(post)

        elif account.provider == SocialAccount.PROVIDER_TIKTOK:
            videos = tt_service.get_video_list(account.access_token, max_count=20)
            for v in videos:
                vid_id  = v.get('id', '')
                pub_at  = None
                if v.get('create_time'):
                    try:
                        pub_at = timezone.datetime.utcfromtimestamp(v['create_time']).replace(tzinfo=timezone.utc)
                    except Exception:
                        pass
                post, _ = SocialPost.objects.update_or_create(
                    account=account,
                    platform_post_id=vid_id,
                    defaults={
                        'provider':      account.provider,
                        'title':         (v.get('title') or v.get('video_description') or '')[:512],
                        'description':   v.get('video_description', '')[:2000],
                        'thumbnail_url': v.get('cover_image_url', ''),
                        'post_url':      v.get('embed_link', ''),
                        'post_type':     SocialPost.POST_TYPE_VIDEO,
                        'published_at':  pub_at,
                        'duration_sec':  v.get('duration', 0),
                        'views':         v.get('view_count', 0),
                        'likes':         v.get('like_count', 0),
                        'comments':      v.get('comment_count', 0),
                        'shares':        v.get('share_count', 0),
                    },
                )
                saved.append(post)

        elif account.provider == SocialAccount.PROVIDER_TWITTER:
            me     = tw_service.get_me(account.access_token)
            tweets = tw_service.get_user_tweets(me['id'], account.access_token, max_results=20)
            username = account.extra_data.get('username', '')
            for t in tweets:
                m = t.get('public_metrics', {})
                pub_at = None
                if t.get('created_at'):
                    try:
                        pub_at = dtparser.parse(t['created_at'])
                    except Exception:
                        pass
                post, _ = SocialPost.objects.update_or_create(
                    account=account,
                    platform_post_id=t['id'],
                    defaults={
                        'provider':     account.provider,
                        'title':        t.get('text', '')[:512],
                        'post_url':     f'https://twitter.com/{username}/status/{t["id"]}' if username else '',
                        'post_type':    SocialPost.POST_TYPE_POST,
                        'published_at': pub_at,
                        'likes':        m.get('like_count', 0),
                        'comments':     m.get('reply_count', 0),
                        'shares':       m.get('retweet_count', 0) + m.get('quote_count', 0),
                        'views':        m.get('impression_count', 0),
                    },
                )
                saved.append(post)

    except Exception:
        pass

    return saved


def _serialize_post(post, account_name='') -> dict:
    return {
        'id':              post.id,
        'provider':        post.provider,
        'platform_post_id': post.platform_post_id,
        'title':           post.title,
        'description':     post.description,
        'thumbnail_url':   post.thumbnail_url,
        'post_url':        post.post_url,
        'post_type':       post.post_type,
        'published_at':    post.published_at,
        'duration_sec':    post.duration_sec,
        'views':           post.views,
        'likes':           post.likes,
        'comments':        post.comments,
        'shares':          post.shares,
        'engagement':      post.engagement,
        'account_name':    account_name or post.account.extra_data.get('name', ''),
        'synced_at':       post.synced_at,
    }


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_social_posts(request):
    """
    GET /api/integrations/social/posts/
    Optional filters: ?provider=youtube&limit=50
    Returns stored posts ordered by published_at desc.
    """
    provider = request.query_params.get('provider')
    limit    = min(int(request.query_params.get('limit', 100)), 200)

    accounts = SocialAccount.objects.filter(user=request.user)
    qs = SocialPost.objects.filter(account__in=accounts).select_related('account')
    if provider:
        qs = qs.filter(provider=provider)
    qs = qs.order_by('-published_at')[:limit]

    # Build account_name lookup
    acc_names = {a.id: _serialize_account(a)['name'] for a in accounts}
    posts = [_serialize_post(p, acc_names.get(p.account_id, '')) for p in qs]
    return Response({'posts': posts, 'total': len(posts)})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def sync_social_posts(request):
    """
    POST /api/integrations/social/posts/sync/
    Optional: ?provider=youtube  to sync only one platform.
    Fetches posts from the platform APIs and stores them in DB.
    """
    provider_filter = request.query_params.get('provider')
    accounts = SocialAccount.objects.filter(user=request.user)
    if provider_filter:
        accounts = accounts.filter(provider=provider_filter)

    results = []
    for account in accounts:
        saved = _upsert_posts_for_account(account)
        results.append({
            'provider': account.provider,
            'saved':    len(saved),
        })

    return Response({'results': results, 'detail': 'Sincronización completada.'})
