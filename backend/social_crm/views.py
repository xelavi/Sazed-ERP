from django.db import transaction
from django.db.models import (
    DecimalField,
    ExpressionWrapper,
    F,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.mixins import CompanyMixin

from .filters import (
    AlertFilter,
    CampaignFilter,
    CollaborationFilter,
    InfluencerFilter,
    PaidAdSetFilter,
    SocialAccountFilter,
    SocialPostFilter,
    TrackedLinkFilter,
)
from .models import (
    Alert,
    Campaign,
    CampaignChannel,
    Collaboration,
    CollaborationEvidence,
    CollaborationPublication,
    Influencer,
    PaidAdSet,
    SocialAccount,
    SocialAccountSnapshot,
    SocialPost,
    TrackedLink,
)
from .serializers import (
    AlertSerializer,
    AlertWriteSerializer,
    CampaignDetailSerializer,
    CampaignListSerializer,
    CampaignWriteSerializer,
    CollaborationDetailSerializer,
    CollaborationEvidenceSerializer,
    CollaborationListSerializer,
    CollaborationPublicationSerializer,
    CollaborationWriteSerializer,
    InfluencerDetailSerializer,
    InfluencerListSerializer,
    InfluencerWriteSerializer,
    PaidAdSetSerializer,
    PaidAdSetWriteSerializer,
    SocialAccountDetailSerializer,
    SocialAccountListSerializer,
    SocialAccountSnapshotSerializer,
    SocialAccountWriteSerializer,
    SocialPostDetailSerializer,
    SocialPostListSerializer,
    SocialPostWriteSerializer,
    TrackedLinkDetailSerializer,
    TrackedLinkListSerializer,
    TrackedLinkWriteSerializer,
)


# ── Social Accounts ───────────────────────────────────────────────────────────


class SocialAccountViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset         = SocialAccount.objects.all()
    filterset_class  = SocialAccountFilter
    ordering_fields  = ['name', 'platform', 'followers', 'updated_at']
    ordering         = ['platform', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return SocialAccountListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return SocialAccountWriteSerializer
        return SocialAccountDetailSerializer

    @action(detail=True, methods=['get', 'post'], url_path='snapshots')
    def snapshots(self, request, pk=None):
        account = self.get_object()
        if request.method == 'GET':
            qs = account.snapshots.order_by('-snapshot_date')
            serializer = SocialAccountSnapshotSerializer(qs, many=True)
            return Response(serializer.data)
        serializer = SocialAccountSnapshotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(account=account)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ── Campaigns ─────────────────────────────────────────────────────────────────


class CampaignViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset        = Campaign.objects.all()
    filterset_class = CampaignFilter
    ordering_fields = ['name', 'start_date', 'end_date', 'status', 'total_budget']
    ordering        = ['-start_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return CampaignListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return CampaignWriteSerializer
        return CampaignDetailSerializer

    def perform_destroy(self, instance):
        """
        Esborra la campanya i el contingut que li pertany en exclusiva.
        Collaboration i PaidAdSet tenen on_delete=PROTECT, de manera que
        cal eliminar-los explícitament. Els SocialPost es desvinculen
        (campaign=NULL via SET_NULL) i es conserven com a contingut orgànic.
        """
        with transaction.atomic():
            instance.tracked_links.all().delete()
            instance.collaborations.all().delete()
            instance.ad_sets.all().delete()
            instance.delete()

    @action(detail=True, methods=['get'], url_path='channel-breakdown')
    def channel_breakdown(self, request, pk=None):
        """
        Desglossament per canal derivat de les dades reals:
          - owned      → SocialPost
          - influencers → Collaboration + TrackedLink
          - paid       → PaidAdSet
        Els totals s'agreguen aquí, mai s'emmagatzemen a Campaign.
        """
        campaign = self.get_object()

        def _sum(qs, field):
            # output_field explícit: Sum d'un DecimalField + Value(0) enter
            # provoca un FieldError de "mixed types"; forcem Decimal i el
            # tornem com a int/float net per no barrejar Decimal i float als totals.
            v = qs.aggregate(v=Coalesce(
                Sum(field), Value(0),
                output_field=DecimalField(max_digits=20, decimal_places=2),
            ))['v'] or 0
            f = float(v)
            return int(f) if f.is_integer() else f

        posts   = SocialPost.objects.filter(campaign=campaign)
        collabs = Collaboration.objects.filter(campaign=campaign)
        ads     = PaidAdSet.objects.filter(campaign=campaign)
        organic_links = TrackedLink.objects.filter(campaign=campaign, collaboration__isnull=True)

        owned = {
            'channel': CampaignChannel.OWNED,
            'label':   CampaignChannel.OWNED.label,
            'items':   posts.count(),
            'reach':       _sum(posts, 'reach'),
            'impressions': _sum(posts, 'impressions'),
            'clicks':      _sum(posts, 'clicks'),
            'conversions': _sum(organic_links, 'purchases'),
            'sales':       _sum(organic_links, 'revenue'),
            'cost': 0,
        }
        influencers = {
            'channel': CampaignChannel.INFLUENCERS,
            'label':   CampaignChannel.INFLUENCERS.label,
            'items':   collabs.count(),
            'reach':       _sum(collabs, 'actual_reach'),
            'impressions': _sum(collabs, 'actual_impressions'),
            'views':       _sum(collabs, 'actual_views'),
            'clicks':      _sum(
                TrackedLink.objects.filter(campaign=campaign, collaboration__isnull=False),
                'clicks',
            ),
            'conversions': _sum(
                TrackedLink.objects.filter(campaign=campaign, collaboration__isnull=False),
                'purchases',
            ),
            'sales': float(_sum(
                TrackedLink.objects.filter(campaign=campaign, collaboration__isnull=False),
                'revenue',
            )),
            'cost': float(_sum(collabs, 'agreed_cost')),
        }
        paid = {
            'channel': CampaignChannel.PAID,
            'label':   CampaignChannel.PAID.label,
            'items':   ads.count(),
            'reach': 0,
            'impressions': _sum(ads, 'impressions'),
            'clicks':      _sum(ads, 'clicks'),
            'conversions': _sum(ads, 'conversions'),
            'sales':   float(_sum(ads, 'sales_revenue')),
            'cost':    float(_sum(ads, 'spend_amount')),
        }

        channels = [owned, influencers, paid]
        for ch in channels:
            ch['roas'] = round(ch['sales'] / ch['cost'], 4) if ch.get('cost') else 0

        totals = {
            key: sum(ch.get(key, 0) for ch in channels)
            for key in ('reach', 'impressions', 'clicks', 'conversions', 'sales', 'cost')
        }
        totals['roas'] = round(totals['sales'] / totals['cost'], 4) if totals['cost'] else 0

        return Response({'channels': channels, 'totals': totals})


# ── Influencers ───────────────────────────────────────────────────────────────


class InfluencerViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset        = Influencer.objects.prefetch_related('platform_presences')
    filterset_class = InfluencerFilter
    ordering_fields = ['name', 'alias', 'status', 'primary_platform', 'created_at']
    ordering        = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return InfluencerListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return InfluencerWriteSerializer
        return InfluencerDetailSerializer


# ── Social Posts ──────────────────────────────────────────────────────────────


class SocialPostViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset        = SocialPost.objects.select_related('account', 'campaign', 'product')
    filterset_class = SocialPostFilter
    ordering_fields = ['published_at', 'reach', 'engagement_rate', 'platform']
    ordering        = ['-published_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return SocialPostListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return SocialPostWriteSerializer
        return SocialPostDetailSerializer


# ── Collaborations ────────────────────────────────────────────────────────────


class CollaborationViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset        = Collaboration.objects.select_related(
        'campaign', 'influencer', 'platform_presence',
    ).prefetch_related('publications', 'evidences', 'tracked_links')
    filterset_class = CollaborationFilter
    ordering_fields = ['created_at', 'publish_date', 'agreed_cost', 'status']
    ordering        = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return CollaborationListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return CollaborationWriteSerializer
        return CollaborationDetailSerializer

    @action(detail=True, methods=['post'], url_path='recalculate')
    def recalculate(self, request, pk=None):
        """Recalcula actual_* a partir de les publicacions."""
        collab = self.get_object()
        collab.recalculate_actuals()
        return Response(CollaborationDetailSerializer(collab, context={'request': request}).data)

    @action(detail=True, methods=['get', 'post'], url_path='publications')
    def publications(self, request, pk=None):
        collab = self.get_object()
        if request.method == 'GET':
            serializer = CollaborationPublicationSerializer(collab.publications.all(), many=True)
            return Response(serializer.data)
        serializer = CollaborationPublicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pub = serializer.save(
            collaboration=collab,
            uploaded_by=request.user,
            uploaded_at=timezone.now(),
        )
        collab.recalculate_actuals()
        return Response(CollaborationPublicationSerializer(pub).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'], url_path='evidences')
    def evidences(self, request, pk=None):
        collab = self.get_object()
        if request.method == 'GET':
            serializer = CollaborationEvidenceSerializer(collab.evidences.all(), many=True)
            return Response(serializer.data)
        serializer = CollaborationEvidenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(collaboration=collab, uploaded_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CollaborationPublicationViewSet(viewsets.ModelViewSet):
    """
    CRUD directe per a publicacions individuals, accessible per URL pròpia.
    En canviar mètriques, recalcula automàticament els totals de la col·laboració pare.
    """
    queryset           = CollaborationPublication.objects.select_related('collaboration')
    serializer_class   = CollaborationPublicationSerializer

    def get_queryset(self):
        company = getattr(self.request, 'company', None)
        if company:
            return self.queryset.filter(collaboration__company=company)
        return self.queryset.none()

    def perform_update(self, serializer):
        pub = serializer.save()
        pub.collaboration.recalculate_actuals()

    def perform_destroy(self, instance):
        collab = instance.collaboration
        instance.delete()
        collab.recalculate_actuals()


# ── Tracked Links ─────────────────────────────────────────────────────────────


class TrackedLinkViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset        = TrackedLink.objects.select_related('campaign', 'collaboration')
    filterset_class = TrackedLinkFilter
    ordering_fields = ['created_at', 'clicks', 'revenue', 'name']
    ordering        = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return TrackedLinkListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return TrackedLinkWriteSerializer
        return TrackedLinkDetailSerializer


# ── Paid Ad Sets ──────────────────────────────────────────────────────────────


class PaidAdSetViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset        = PaidAdSet.objects.select_related('campaign')
    filterset_class = PaidAdSetFilter
    ordering_fields = ['start_date', 'budget_amount', 'spend_amount', 'conversions']
    ordering        = ['-start_date']

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return PaidAdSetWriteSerializer
        return PaidAdSetSerializer


# ── Alerts ────────────────────────────────────────────────────────────────────


class AlertViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset        = Alert.objects.select_related(
        'responsible', 'social_account', 'tracked_link',
        'campaign', 'post', 'collaboration',
    )
    filterset_class = AlertFilter
    ordering_fields = ['alert_date', 'severity', 'status', 'created_at']
    ordering        = ['-alert_date', '-created_at']

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return AlertWriteSerializer
        return AlertSerializer

    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.status      = 'resolved'
        alert.resolved_at = timezone.now()
        alert.save(update_fields=['status', 'resolved_at'])
        return Response(AlertSerializer(alert, context={'request': request}).data)


# ── Dashboard KPI ─────────────────────────────────────────────────────────────


class SocialCrmDashboardView(APIView):
    """
    Vista de resum per al dashboard del Social CRM.
    Tots els valors es calculen en temps de consulta; cap d'ells es
    guarda a la base de dades per evitar inconsistències.
    """

    def get(self, request):
        company = getattr(request, 'company', None)
        if not company:
            return Response({'detail': 'Company no trobada.'}, status=400)

        accounts = SocialAccount.objects.filter(company=company)
        posts    = SocialPost.objects.filter(company=company)
        collabs  = Collaboration.objects.filter(company=company, status='active')
        links    = TrackedLink.objects.filter(company=company)

        total_followers   = accounts.aggregate(v=Coalesce(Sum('followers'), Value(0)))['v']
        total_reach       = posts.aggregate(v=Coalesce(Sum('reach'), Value(0)))['v']
        total_clicks      = links.aggregate(v=Coalesce(Sum('clicks'), Value(0)))['v']
        total_conversions = links.aggregate(v=Coalesce(Sum('purchases'), Value(0)))['v']
        attributed_sales  = links.aggregate(
            v=Coalesce(Sum('revenue'), Value(0, output_field=DecimalField()))
        )['v']
        active_collabs    = collabs.count()

        avg_engagement = posts.aggregate(
            v=Coalesce(Sum('engagement_rate'), Value(0, output_field=DecimalField()))
        )['v']
        posts_count = posts.count()
        avg_engagement = round(float(avg_engagement) / posts_count, 2) if posts_count else 0

        pending_alerts = Alert.objects.filter(
            company=company, status__in=['pending', 'assigned'],
        ).count()

        return Response({
            'total_followers':        total_followers,
            'total_reach':            total_reach,
            'avg_engagement':         avg_engagement,
            'total_clicks':           total_clicks,
            'total_conversions':      total_conversions,
            'attributed_sales':       float(attributed_sales),
            'active_collaborations':  active_collabs,
            'pending_alerts':         pending_alerts,
        })
