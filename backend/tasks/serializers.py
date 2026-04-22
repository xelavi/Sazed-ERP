from rest_framework import serializers

from .models import TaskTag, Task


class TaskTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTag
        fields = ['id', 'label', 'color_class']


class TaskSerializer(serializers.ModelSerializer):
    tags = TaskTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        source='tags', many=True, write_only=True,
        queryset=TaskTag.objects.all(), required=False,
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'completed', 'tags', 'tag_ids',
            'due_date', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        task = Task.objects.create(**validated_data)
        if tags:
            task.tags.set(tags)
        return task

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance
