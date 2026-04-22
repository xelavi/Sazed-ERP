from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TaskTagViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'tags', TaskTagViewSet)
router.register(r'', TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
