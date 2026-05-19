"""
Views for accounts app — auth, profile, companies, members.
"""

from django.contrib.auth import login, logout
from django.utils.text import slugify
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Q
from django.utils import timezone

from .models import User, Company, Membership, Notification, Message, Invitation, SocialAccount, SystemSettings
from .services import facebook as fb_service
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
    if membership:
        company_data = CompanySerializer(membership.company).data
        role = membership.role

    return {
        'user': UserSerializer(user).data,
        'company': company_data,
        'role': role,
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
    if not request.user.is_staff:
        raise PermissionDenied('Solo staff puede acceder a configuración del sistema.')

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
