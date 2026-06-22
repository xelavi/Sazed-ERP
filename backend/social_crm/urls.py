from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AlertViewSet,
    CampaignViewSet,
    CollaborationPublicationViewSet,
    CollaborationViewSet,
    InfluencerViewSet,
    PaidAdSetViewSet,
    SocialAccountViewSet,
    SocialCrmDashboardView,
    SocialPostViewSet,
    TrackedLinkViewSet,
)

router = DefaultRouter()
router.register(r'accounts',      SocialAccountViewSet,          basename='social-account')
router.register(r'campaigns',     CampaignViewSet,               basename='social-campaign')
router.register(r'influencers',   InfluencerViewSet,             basename='influencer')
router.register(r'posts',         SocialPostViewSet,             basename='social-post')
router.register(r'collaborations',CollaborationViewSet,          basename='collaboration')
router.register(r'publications',  CollaborationPublicationViewSet, basename='collab-publication')
router.register(r'links',         TrackedLinkViewSet,            basename='tracked-link')
router.register(r'ad-sets',       PaidAdSetViewSet,              basename='paid-adset')
router.register(r'alerts',        AlertViewSet,                  basename='social-alert')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', SocialCrmDashboardView.as_view(), name='social-crm-dashboard'),
]
