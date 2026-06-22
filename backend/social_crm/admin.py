from django.contrib import admin

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

class SocialAccountSnapshotInline(admin.TabularInline):
    model  = SocialAccountSnapshot
    extra  = 0
    readonly_fields = ['created_at']
    ordering = ['-snapshot_date']


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display   = ['platform', 'username', 'name', 'status', 'followers', 'company', 'last_synced_at']
    list_filter    = ['platform', 'status', 'company']
    search_fields  = ['username', 'name']
    inlines        = [SocialAccountSnapshotInline]


# ── Campaigns ─────────────────────────────────────────────────────────────────

class CampaignChannelBudgetInline(admin.TabularInline):
    model = CampaignChannelBudget
    extra = 0


class CampaignTargetInline(admin.TabularInline):
    model = CampaignTarget
    extra = 0


class CampaignTimelineEventInline(admin.TabularInline):
    model = CampaignTimelineEvent
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display  = ['name', 'objective', 'status', 'start_date', 'end_date', 'total_budget', 'company']
    list_filter   = ['status', 'objective', 'company']
    search_fields = ['name']
    inlines       = [CampaignChannelBudgetInline, CampaignTargetInline, CampaignTimelineEventInline]


# ── Influencers ───────────────────────────────────────────────────────────────

class InfluencerPlatformPresenceInline(admin.TabularInline):
    model = InfluencerPlatformPresence
    extra = 0


@admin.register(Influencer)
class InfluencerAdmin(admin.ModelAdmin):
    list_display  = ['alias', 'name', 'primary_platform', 'niche', 'status', 'company']
    list_filter   = ['status', 'primary_platform', 'company']
    search_fields = ['name', 'alias']
    inlines       = [InfluencerPlatformPresenceInline]


# ── Social Posts ──────────────────────────────────────────────────────────────

@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    list_display  = ['title', 'platform', 'content_type', 'published_at', 'reach', 'engagement_rate', 'company']
    list_filter   = ['platform', 'content_type', 'company']
    search_fields = ['title']
    date_hierarchy = 'published_at'


# ── Collaborations ────────────────────────────────────────────────────────────

class CollaborationPublicationInline(admin.TabularInline):
    model    = CollaborationPublication
    extra    = 0
    readonly_fields = ['created_at']


class CollaborationEvidenceInline(admin.TabularInline):
    model = CollaborationEvidence
    extra = 0
    readonly_fields = ['uploaded_at']


@admin.register(Collaboration)
class CollaborationAdmin(admin.ModelAdmin):
    list_display  = [
        'influencer', 'campaign', 'content_format', 'publish_date',
        'agreed_cost', 'status', 'company',
    ]
    list_filter   = ['status', 'company']
    search_fields = ['influencer__name', 'influencer__alias', 'campaign__name']
    inlines       = [CollaborationPublicationInline, CollaborationEvidenceInline]
    readonly_fields = [
        'actual_reach', 'actual_impressions', 'actual_views',
        'actual_likes', 'actual_comments', 'actual_shares',
    ]


# ── Tracked Links ─────────────────────────────────────────────────────────────

@admin.register(TrackedLink)
class TrackedLinkAdmin(admin.ModelAdmin):
    list_display  = ['name', 'campaign', 'origin_platform', 'is_active', 'clicks', 'purchases', 'revenue']
    list_filter   = ['is_active', 'origin_platform', 'company']
    search_fields = ['name', 'utm_campaign', 'utm_content']


# ── Paid Ad Sets ──────────────────────────────────────────────────────────────

@admin.register(PaidAdSet)
class PaidAdSetAdmin(admin.ModelAdmin):
    list_display  = ['name', 'campaign', 'ad_platform', 'status', 'budget_amount', 'spend_amount', 'conversions']
    list_filter   = ['ad_platform', 'status', 'company']
    search_fields = ['name']


# ── Alerts ────────────────────────────────────────────────────────────────────

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display  = ['alert_type', 'severity', 'status', 'alert_date', 'responsible', 'company']
    list_filter   = ['alert_type', 'severity', 'status', 'company']
    search_fields = ['description']
    date_hierarchy = 'alert_date'
