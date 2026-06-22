"""URL configuration for accounts app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('companies', views.CompanyViewSet, basename='company')
router.register('notifications', views.NotificationViewSet, basename='notification')
router.register('messages', views.MessageViewSet, basename='message')
router.register('invitations', views.InvitationViewSet, basename='invitation')

urlpatterns = [
    # Auth
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/me/', views.me_view, name='me'),
    path('auth/profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('auth/facebook/', views.FacebookLoginView.as_view(), name='auth-facebook'),

    # Inbox
    path('users/search/', views.user_search, name='user-search'),
    path('inbox/summary/', views.inbox_summary, name='inbox-summary'),

    # Facebook / Instagram integration
    path('integrations/facebook/connect/', views.facebook_connect, name='fb-connect'),
    path('integrations/facebook/status/', views.facebook_status, name='fb-status'),
    path('integrations/facebook/pages/', views.facebook_pages, name='fb-pages'),
    path('integrations/facebook/instagram/', views.facebook_instagram, name='fb-instagram'),
    path('integrations/facebook/disconnect/', views.facebook_disconnect, name='fb-disconnect'),

    # System settings — Facebook
    path('settings/facebook/app-id/', views.facebook_app_config, name='settings-facebook-appid'),
    path('settings/facebook/', views.system_settings_facebook, name='settings-facebook'),

    # YouTube / Google integration
    path('integrations/youtube/connect/', views.youtube_connect, name='youtube-connect'),
    path('integrations/youtube/status/', views.youtube_status, name='youtube-status'),
    path('integrations/youtube/disconnect/', views.youtube_disconnect, name='youtube-disconnect'),
    path('integrations/youtube/channels/', views.youtube_channels, name='youtube-channels'),

    # System settings — YouTube
    path('settings/youtube/client-id/', views.youtube_app_config, name='settings-youtube-clientid'),
    path('settings/youtube/', views.system_settings_youtube, name='settings-youtube'),

    # X (Twitter) integration — popup OAuth flow
    path('integrations/twitter/init/', views.twitter_init, name='twitter-init'),
    path('integrations/twitter/callback/', views.twitter_callback, name='twitter-callback'),
    path('integrations/twitter/status/', views.twitter_status, name='twitter-status'),
    path('integrations/twitter/disconnect/', views.twitter_disconnect, name='twitter-disconnect'),
    path('integrations/twitter/metrics/', views.twitter_metrics, name='twitter-metrics'),

    # System settings — Twitter
    path('settings/twitter/client-id/', views.twitter_app_config, name='settings-twitter-clientid'),
    path('settings/twitter/', views.system_settings_twitter, name='settings-twitter'),

    # TikTok integration — popup OAuth flow
    path('integrations/tiktok/init/', views.tiktok_init, name='tiktok-init'),
    path('integrations/tiktok/callback/', views.tiktok_callback, name='tiktok-callback'),
    path('integrations/tiktok/status/', views.tiktok_status, name='tiktok-status'),
    path('integrations/tiktok/disconnect/', views.tiktok_disconnect, name='tiktok-disconnect'),
    path('integrations/tiktok/metrics/', views.tiktok_metrics, name='tiktok-metrics'),

    # System settings — TikTok
    path('settings/tiktok/client-key/', views.tiktok_app_config, name='settings-tiktok-clientkey'),
    path('settings/tiktok/', views.system_settings_tiktok, name='settings-tiktok'),

    # Social accounts list + stats sync
    path('integrations/social/accounts/', views.social_accounts_list, name='social-accounts'),
    path('integrations/social/sync/', views.sync_social_stats, name='social-sync'),

    # Social posts (videos)
    path('integrations/social/posts/', views.list_social_posts, name='social-posts'),
    path('integrations/social/posts/sync/', views.sync_social_posts, name='social-posts-sync'),

    # Companies, notifications, messages, invitations
    path('', include(router.urls)),
]
