from rest_framework import serializers

from .models import (
    Alert,
    Campaign,
    CampaignChannelBudget,
    CampaignTarget,
    CampaignTimelineEvent,
    Collaboration,
    CollaborationEvidence,
    CollaborationPublication,
    Influencer,
    InfluencerPlatformPresence,
    PaidAdSet,
    SocialAccount,
    SocialAccountSnapshot,
    SocialPost,
    TrackedLink,
)


# ── Social Accounts ───────────────────────────────────────────────────────────


class SocialAccountListSerializer(serializers.ModelSerializer):
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    status_display   = serializers.CharField(source='get_status_display', read_only=True)
    responsible_name = serializers.SerializerMethodField()

    class Meta:
        model  = SocialAccount
        fields = [
            'id', 'platform', 'platform_display', 'name', 'username',
            'status', 'status_display', 'followers', 'posts_count',
            'responsible', 'responsible_name', 'last_synced_at',
        ]

    def get_responsible_name(self, obj):
        return obj.responsible.full_name if obj.responsible else None


class SocialAccountDetailSerializer(SocialAccountListSerializer):
    class Meta(SocialAccountListSerializer.Meta):
        fields = SocialAccountListSerializer.Meta.fields + ['observations', 'created_at', 'updated_at']


class SocialAccountWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SocialAccount
        fields = [
            'platform', 'name', 'username', 'status',
            'followers', 'posts_count', 'responsible', 'observations',
        ]


class SocialAccountSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SocialAccountSnapshot
        fields = [
            'id', 'account', 'snapshot_date', 'followers', 'posts_count',
            'avg_engagement_rate', 'avg_reach', 'created_at',
        ]
        read_only_fields = ['created_at']


# ── Campaigns ─────────────────────────────────────────────────────────────────


class CampaignChannelBudgetSerializer(serializers.ModelSerializer):
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)

    class Meta:
        model  = CampaignChannelBudget
        fields = ['id', 'channel', 'channel_display', 'budget_amount']


class CampaignTargetSerializer(serializers.ModelSerializer):
    metric_display = serializers.CharField(source='get_metric_key_display', read_only=True)

    class Meta:
        model  = CampaignTarget
        fields = ['id', 'metric_key', 'metric_display', 'target_value']


class CampaignTimelineEventSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)

    class Meta:
        model  = CampaignTimelineEvent
        fields = ['id', 'event_date', 'description', 'event_type', 'event_type_display']


class CampaignListSerializer(serializers.ModelSerializer):
    objective_display = serializers.CharField(source='get_objective_display', read_only=True)
    status_display    = serializers.CharField(source='get_status_display', read_only=True)
    responsible_name  = serializers.SerializerMethodField()

    class Meta:
        model  = Campaign
        fields = [
            'id', 'name', 'objective', 'objective_display', 'status', 'status_display',
            'start_date', 'end_date', 'total_budget', 'responsible', 'responsible_name',
        ]

    def get_responsible_name(self, obj):
        return obj.responsible.full_name if obj.responsible else None


class CampaignDetailSerializer(CampaignListSerializer):
    channel_budgets  = CampaignChannelBudgetSerializer(many=True, read_only=True)
    targets          = CampaignTargetSerializer(many=True, read_only=True)
    timeline_events  = CampaignTimelineEventSerializer(many=True, read_only=True)

    class Meta(CampaignListSerializer.Meta):
        fields = CampaignListSerializer.Meta.fields + [
            'description', 'channel_budgets', 'targets', 'timeline_events',
            'created_at', 'updated_at',
        ]


class CampaignWriteSerializer(serializers.ModelSerializer):
    channel_budgets = CampaignChannelBudgetSerializer(many=True, required=False)
    targets         = CampaignTargetSerializer(many=True, required=False)
    timeline_events = CampaignTimelineEventSerializer(many=True, required=False)

    class Meta:
        model  = Campaign
        fields = [
            'id', 'name', 'objective', 'status', 'start_date', 'end_date',
            'total_budget', 'description', 'responsible',
            'channel_budgets', 'targets', 'timeline_events',
        ]

    def _save_nested(self, campaign, channel_budgets_data, targets_data, timeline_data):
        if channel_budgets_data is not None:
            campaign.channel_budgets.all().delete()
            for item in channel_budgets_data:
                CampaignChannelBudget.objects.create(campaign=campaign, **item)
        if targets_data is not None:
            campaign.targets.all().delete()
            for item in targets_data:
                CampaignTarget.objects.create(campaign=campaign, **item)
        if timeline_data is not None:
            campaign.timeline_events.all().delete()
            for item in timeline_data:
                CampaignTimelineEvent.objects.create(campaign=campaign, **item)

    def create(self, validated_data):
        channel_budgets = validated_data.pop('channel_budgets', None)
        targets         = validated_data.pop('targets', None)
        timeline_events = validated_data.pop('timeline_events', None)
        campaign = Campaign.objects.create(**validated_data)
        self._save_nested(campaign, channel_budgets, targets, timeline_events)
        return campaign

    def update(self, instance, validated_data):
        channel_budgets = validated_data.pop('channel_budgets', None)
        targets         = validated_data.pop('targets', None)
        timeline_events = validated_data.pop('timeline_events', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self._save_nested(instance, channel_budgets, targets, timeline_events)
        return instance


# ── Influencers ───────────────────────────────────────────────────────────────


class InfluencerPlatformPresenceSerializer(serializers.ModelSerializer):
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)

    class Meta:
        model  = InfluencerPlatformPresence
        fields = [
            'id', 'platform', 'platform_display', 'username', 'followers',
            'avg_engagement_rate', 'avg_reach', 'avg_clicks', 'avg_conversions',
        ]


class InfluencerListSerializer(serializers.ModelSerializer):
    primary_platform_display = serializers.CharField(source='get_primary_platform_display', read_only=True)
    status_display           = serializers.CharField(source='get_status_display', read_only=True)
    collaborations_count     = serializers.SerializerMethodField()
    followers                = serializers.SerializerMethodField()

    class Meta:
        model  = Influencer
        fields = [
            'id', 'name', 'alias', 'photo', 'primary_platform', 'primary_platform_display',
            'niche', 'status', 'status_display', 'contact_email', 'agency_name',
            'country', 'language', 'collaborations_count', 'followers',
            'score_content_quality', 'score_reliability',
            'score_brand_affinity', 'score_reputation_risk',
        ]

    def get_collaborations_count(self, obj):
        return obj.collaborations.count()

    def get_followers(self, obj):
        """Suma de seguidors de totes les plataformes (prefetched al viewset)."""
        return sum(p.followers for p in obj.platform_presences.all())


class InfluencerDetailSerializer(InfluencerListSerializer):
    platform_presences = InfluencerPlatformPresenceSerializer(many=True, read_only=True)

    class Meta(InfluencerListSerializer.Meta):
        fields = InfluencerListSerializer.Meta.fields + [
            'platform_presences', 'notes', 'created_at', 'updated_at',
        ]


class InfluencerWriteSerializer(serializers.ModelSerializer):
    platform_presences = InfluencerPlatformPresenceSerializer(many=True, required=False)

    class Meta:
        model  = Influencer
        fields = [
            'id', 'name', 'alias', 'photo', 'primary_platform', 'niche',
            'contact_email', 'agency_name', 'country', 'language', 'status',
            'score_content_quality', 'score_reliability',
            'score_brand_affinity', 'score_reputation_risk',
            'notes', 'platform_presences',
        ]

    def _save_presences(self, influencer, presences_data):
        if presences_data is None:
            return
        influencer.platform_presences.all().delete()
        for item in presences_data:
            InfluencerPlatformPresence.objects.create(influencer=influencer, **item)

    def create(self, validated_data):
        presences = validated_data.pop('platform_presences', None)
        influencer = Influencer.objects.create(**validated_data)
        self._save_presences(influencer, presences)
        return influencer

    def update(self, instance, validated_data):
        presences = validated_data.pop('platform_presences', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self._save_presences(instance, presences)
        return instance


# ── Social Posts ──────────────────────────────────────────────────────────────


class SocialPostListSerializer(serializers.ModelSerializer):
    platform_display     = serializers.CharField(source='get_platform_display', read_only=True)
    content_type_display = serializers.CharField(source='get_content_type_display', read_only=True)
    account_name         = serializers.CharField(source='account.username', read_only=True)
    campaign_name        = serializers.CharField(source='campaign.name', read_only=True)

    class Meta:
        model  = SocialPost
        fields = [
            'id', 'platform', 'platform_display', 'account', 'account_name',
            'campaign', 'campaign_name', 'title', 'content_type', 'content_type_display',
            'published_at', 'reach', 'impressions', 'clicks', 'engagement_rate',
            'likes', 'comments', 'shares', 'saves', 'views',
        ]


class SocialPostDetailSerializer(SocialPostListSerializer):
    class Meta(SocialPostListSerializer.Meta):
        fields = SocialPostListSerializer.Meta.fields + [
            'product', 'url', 'created_at', 'updated_at',
        ]


class SocialPostWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SocialPost
        fields = [
            'account', 'campaign', 'product', 'platform', 'title', 'content_type',
            'published_at', 'url', 'likes', 'comments', 'shares', 'saves',
            'views', 'reach', 'impressions', 'clicks', 'engagement_rate',
        ]


# ── Collaborations ────────────────────────────────────────────────────────────


class CollaborationPublicationSerializer(serializers.ModelSerializer):
    content_type_display = serializers.CharField(source='get_content_type_display', read_only=True)
    metrics_status_display = serializers.CharField(source='get_metrics_status_display', read_only=True)
    uploaded_by_name     = serializers.SerializerMethodField()
    validated_by_name    = serializers.SerializerMethodField()

    class Meta:
        model  = CollaborationPublication
        fields = [
            'id', 'content_type', 'content_type_display', 'description',
            'publication_date', 'url',
            'reach', 'impressions', 'views', 'likes', 'comments', 'shares',
            'metrics_status', 'metrics_status_display',
            'uploaded_by', 'uploaded_by_name', 'uploaded_at',
            'validated_by', 'validated_by_name', 'validated_at',
            'created_at',
        ]
        read_only_fields = ['created_at']

    def get_uploaded_by_name(self, obj):
        return obj.uploaded_by.full_name if obj.uploaded_by else None

    def get_validated_by_name(self, obj):
        return obj.validated_by.full_name if obj.validated_by else None


class CollaborationEvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CollaborationEvidence
        fields = ['id', 'file', 'label', 'uploaded_at', 'uploaded_by']
        read_only_fields = ['uploaded_at']


class CollaborationListSerializer(serializers.ModelSerializer):
    influencer_name    = serializers.CharField(source='influencer.name', read_only=True)
    influencer_alias   = serializers.CharField(source='influencer.alias', read_only=True)
    campaign_name      = serializers.CharField(source='campaign.name', read_only=True)
    status_display     = serializers.CharField(source='get_status_display', read_only=True)
    platform_label     = serializers.SerializerMethodField()

    class Meta:
        model  = Collaboration
        fields = [
            'id', 'campaign', 'campaign_name', 'influencer', 'influencer_name',
            'influencer_alias', 'platform_presence', 'platform_label',
            'content_format', 'publish_date', 'agreed_cost',
            'discount_code', 'status', 'status_display',
            'actual_reach', 'actual_impressions', 'actual_views',
            'actual_likes', 'actual_comments', 'actual_shares',
        ]

    def get_platform_label(self, obj):
        if obj.platform_presence:
            return obj.platform_presence.get_platform_display()
        return None


class CollaborationDetailSerializer(CollaborationListSerializer):
    publications = CollaborationPublicationSerializer(many=True, read_only=True)
    evidences    = CollaborationEvidenceSerializer(many=True, read_only=True)
    tracked_links = serializers.SerializerMethodField()

    class Meta(CollaborationListSerializer.Meta):
        fields = CollaborationListSerializer.Meta.fields + [
            'deliverables_description',
            'expected_reach', 'expected_clicks', 'expected_conversions',
            'observations', 'recommendation',
            'publications', 'evidences', 'tracked_links',
            'created_at', 'updated_at',
        ]

    def get_tracked_links(self, obj):
        from .serializers import TrackedLinkListSerializer
        return TrackedLinkListSerializer(obj.tracked_links.all(), many=True).data


class CollaborationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Collaboration
        fields = [
            'campaign', 'influencer', 'platform_presence',
            'content_format', 'publish_date', 'agreed_cost',
            'discount_code', 'status', 'deliverables_description',
            'expected_reach', 'expected_clicks', 'expected_conversions',
            'observations', 'recommendation',
        ]

    def validate(self, attrs):
        influencer = attrs.get('influencer', getattr(self.instance, 'influencer', None))
        presence   = attrs.get('platform_presence')
        if presence and presence.influencer != influencer:
            raise serializers.ValidationError(
                'platform_presence ha de pertànyer a l\'influencer seleccionat.'
            )
        return attrs


# ── Tracked Links ─────────────────────────────────────────────────────────────


class TrackedLinkListSerializer(serializers.ModelSerializer):
    campaign_name      = serializers.CharField(source='campaign.name', read_only=True)
    influencer_name    = serializers.SerializerMethodField()
    conversion_rate    = serializers.FloatField(read_only=True)

    class Meta:
        model  = TrackedLink
        fields = [
            'id', 'name', 'campaign', 'campaign_name', 'collaboration',
            'influencer_name', 'origin_platform',
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_content',
            'is_active', 'clicks', 'sessions', 'carts', 'purchases',
            'revenue', 'conversion_rate',
        ]

    def get_influencer_name(self, obj):
        if obj.collaboration and obj.collaboration.influencer:
            return obj.collaboration.influencer.name
        return None


class TrackedLinkDetailSerializer(TrackedLinkListSerializer):
    class Meta(TrackedLinkListSerializer.Meta):
        fields = TrackedLinkListSerializer.Meta.fields + [
            'destination_url', 'utm_term', 'created_at', 'updated_at',
        ]


class TrackedLinkWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = TrackedLink
        fields = [
            'campaign', 'collaboration', 'name', 'destination_url',
            'origin_platform', 'utm_source', 'utm_medium', 'utm_campaign',
            'utm_content', 'utm_term', 'is_active',
            'clicks', 'sessions', 'carts', 'purchases', 'revenue',
        ]

    def validate(self, attrs):
        collab   = attrs.get('collaboration', getattr(self.instance, 'collaboration', None))
        campaign = attrs.get('campaign', getattr(self.instance, 'campaign', None))
        if collab and campaign and collab.campaign != campaign:
            raise serializers.ValidationError(
                'La campanya de la col·laboració ha de coincidir amb la campanya de l\'enllaç.'
            )
        return attrs


# ── Paid Ad Sets ──────────────────────────────────────────────────────────────


class PaidAdSetSerializer(serializers.ModelSerializer):
    ad_platform_display = serializers.CharField(source='get_ad_platform_display', read_only=True)
    status_display      = serializers.CharField(source='get_status_display', read_only=True)
    campaign_name       = serializers.CharField(source='campaign.name', read_only=True)
    ctr  = serializers.FloatField(read_only=True)
    cpc  = serializers.FloatField(read_only=True)
    cpa  = serializers.FloatField(read_only=True)
    roas = serializers.FloatField(read_only=True)

    class Meta:
        model  = PaidAdSet
        fields = [
            'id', 'campaign', 'campaign_name', 'ad_platform', 'ad_platform_display',
            'name', 'status', 'status_display', 'start_date', 'end_date',
            'budget_amount', 'spend_amount',
            'impressions', 'clicks', 'conversions', 'sales_revenue',
            'ctr', 'cpc', 'cpa', 'roas',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class PaidAdSetWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PaidAdSet
        fields = [
            'campaign', 'ad_platform', 'name', 'status', 'start_date', 'end_date',
            'budget_amount', 'spend_amount',
            'impressions', 'clicks', 'conversions', 'sales_revenue',
        ]


# ── Alerts ────────────────────────────────────────────────────────────────────


class AlertSerializer(serializers.ModelSerializer):
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    severity_display   = serializers.CharField(source='get_severity_display', read_only=True)
    status_display     = serializers.CharField(source='get_status_display', read_only=True)
    responsible_name   = serializers.SerializerMethodField()
    entity_label       = serializers.SerializerMethodField()

    class Meta:
        model  = Alert
        fields = [
            'id', 'alert_date', 'alert_type', 'alert_type_display',
            'severity', 'severity_display', 'status', 'status_display',
            'description', 'responsible', 'responsible_name',
            'resolved_at', 'entity_label',
            'social_account', 'tracked_link', 'campaign', 'post', 'collaboration',
            'created_at',
        ]
        read_only_fields = ['created_at']

    def get_responsible_name(self, obj):
        return obj.responsible.full_name if obj.responsible else None

    def get_entity_label(self, obj):
        if obj.social_account:
            return f'Compte: {obj.social_account}'
        if obj.tracked_link:
            return f'Enllaç: {obj.tracked_link.name}'
        if obj.campaign:
            return f'Campanya: {obj.campaign.name}'
        if obj.post:
            return f'Post: {obj.post.title[:60]}'
        if obj.collaboration:
            return f'Col·laboració: {obj.collaboration}'
        return '—'


class AlertWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Alert
        fields = [
            'alert_date', 'alert_type', 'severity', 'status', 'description',
            'responsible', 'resolved_at',
            'social_account', 'tracked_link', 'campaign', 'post', 'collaboration',
        ]

    def validate(self, attrs):
        entity_fields = ['social_account', 'tracked_link', 'campaign', 'post', 'collaboration']
        if not any(attrs.get(f) for f in entity_fields):
            raise serializers.ValidationError(
                'Cal associar l\'alerta a com a mínim una entitat (compte, campanya, post, col·laboració o enllaç).'
            )
        return attrs
