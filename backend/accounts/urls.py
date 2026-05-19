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

    # System settings
    path('settings/facebook/app-id/', views.facebook_app_config, name='settings-facebook-appid'),
    path('settings/facebook/', views.system_settings_facebook, name='settings-facebook'),

    # Companies, notifications, messages, invitations
    path('', include(router.urls)),
]
