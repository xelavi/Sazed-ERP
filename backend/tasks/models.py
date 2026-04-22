from django.db import models


class TaskTag(models.Model):
    """Etiqueta de tarea con color."""

    label = models.CharField(max_length=50)
    color_class = models.CharField(max_length=30)  # "tag-purple", "tag-red", etc.

    class Meta:
        ordering = ['label']

    def __str__(self):
        return self.label


class Task(models.Model):
    """Tarea personal del dashboard."""

    class Status(models.TextChoices):
        UPCOMING = 'upcoming', 'Próxima'
        OVERDUE = 'overdue', 'Vencida'
        COMPLETED = 'completed', 'Completada'

    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='tasks', null=True, blank=True,
    )
    title = models.CharField(max_length=300)
    completed = models.BooleanField(default=False)
    tags = models.ManyToManyField(TaskTag, blank=True, related_name='tasks')
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=15, choices=Status.choices, default='upcoming',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', '-created_at']

    def __str__(self):
        return self.title
