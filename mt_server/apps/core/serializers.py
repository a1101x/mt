from rest_framework import serializers


class StringListField(serializers.ListField):
    """
    List of strings.
    """
    child = serializers.CharField()


class WorkerSerializer(serializers.Serializer):
    """
    Serializer for workers.
    """
    shutdown = StringListField()


class CancelConsumerSerializer(serializers.Serializer):
    """
    Serializer for cancel consumers.
    """
    consumer = serializers.CharField(max_length=255)
    destination = StringListField()
