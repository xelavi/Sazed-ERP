from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.mixins import CompanyMixin
from .models import Task, TaskTag
from .serializers import TaskSerializer, TaskTagSerializer


class TaskTagViewSet(viewsets.ModelViewSet):
    queryset = TaskTag.objects.all()
    serializer_class = TaskTagSerializer
    pagination_class = None


class TaskViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset = Task.objects.prefetch_related('tags').all()
    serializer_class = TaskSerializer
    filterset_fields = ['status', 'completed']
    ordering_fields = ['due_date', 'created_at']
    ordering = ['due_date', '-created_at']

    @action(detail=True, methods=['patch'])
    def toggle(self, request, pk=None):
        """Toggle completado."""
        task = self.get_object()
        task.completed = not task.completed
        task.status = 'completed' if task.completed else 'upcoming'
        task.save(update_fields=['completed', 'status', 'updated_at'])
        serializer = TaskSerializer(task)
        return Response(serializer.data)
