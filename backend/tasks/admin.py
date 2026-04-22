from django.contrib import admin

from .models import TaskTag, Task


@admin.register(TaskTag)
class TaskTagAdmin(admin.ModelAdmin):
    list_display = ['label', 'color_class']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'completed', 'status', 'due_date', 'created_at']
    list_filter = ['status', 'completed']
    search_fields = ['title']
