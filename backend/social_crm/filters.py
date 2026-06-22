import django_filters

from .models import (
    Alert,
    Campaign,
    Collaboration,
    Influencer,
    PaidAdSet,
    SocialAccount,
    SocialPost,
    TrackedLink,
)


class SocialAccountFilter(django_filters.FilterSet):
    platform = django_filters.CharFilter()
    status   = django_filters.CharFilter()

    class Meta:
        model  = SocialAccount
        fields = ['platform', 'status']


class CampaignFilter(django_filters.FilterSet):
    status    = django_filters.CharFilter()
    objective = django_filters.CharFilter()
    start_after  = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_before = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_after    = django_filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_before   = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')

    class Meta:
        model  = Campaign
        fields = ['status', 'objective']


class InfluencerFilter(django_filters.FilterSet):
    status           = django_filters.CharFilter()
    primary_platform = django_filters.CharFilter()
    niche            = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model  = Influencer
        fields = ['status', 'primary_platform', 'niche']


class SocialPostFilter(django_filters.FilterSet):
    platform     = django_filters.CharFilter()
    content_type = django_filters.CharFilter()
    campaign     = django_filters.NumberFilter()
    published_after  = django_filters.DateFilter(field_name='published_at', lookup_expr='gte')
    published_before = django_filters.DateFilter(field_name='published_at', lookup_expr='lte')

    class Meta:
        model  = SocialPost
        fields = ['platform', 'content_type', 'campaign']


class CollaborationFilter(django_filters.FilterSet):
    campaign   = django_filters.NumberFilter()
    influencer = django_filters.NumberFilter()
    status     = django_filters.CharFilter()

    class Meta:
        model  = Collaboration
        fields = ['campaign', 'influencer', 'status']


class TrackedLinkFilter(django_filters.FilterSet):
    campaign      = django_filters.NumberFilter()
    collaboration = django_filters.NumberFilter()
    is_active     = django_filters.BooleanFilter()
    origin_platform = django_filters.CharFilter()

    class Meta:
        model  = TrackedLink
        fields = ['campaign', 'collaboration', 'is_active', 'origin_platform']


class PaidAdSetFilter(django_filters.FilterSet):
    campaign    = django_filters.NumberFilter()
    ad_platform = django_filters.CharFilter()
    status      = django_filters.CharFilter()

    class Meta:
        model  = PaidAdSet
        fields = ['campaign', 'ad_platform', 'status']


class AlertFilter(django_filters.FilterSet):
    alert_type = django_filters.CharFilter()
    severity   = django_filters.CharFilter()
    status     = django_filters.CharFilter()
    date_after  = django_filters.DateFilter(field_name='alert_date', lookup_expr='gte')
    date_before = django_filters.DateFilter(field_name='alert_date', lookup_expr='lte')

    class Meta:
        model  = Alert
        fields = ['alert_type', 'severity', 'status']
