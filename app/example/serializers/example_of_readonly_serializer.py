"""Example of a readonly serializer with computed fields."""
from rest_framework import serializers
from example.models import ExampleOfFetchLog

class ExampleOfReadonlySerializer(serializers.ModelSerializer):
    """Example of a readonly serializer with computed fields."""

    source_name = serializers.CharField(source='source', read_only=True)
    duration = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()

    class Meta:
        model = ExampleOfFetchLog
        fields = [
            'id', 'source', 'source_name', 'status',
            'started_at', 'completed_at', 'items_fetched',
            'items_saved', 'error_message', 'query_params',
            'metadata', 'raw_data_file', 'duration', 'success_rate'
        ]
        read_only_fields = fields

    def get_duration(self, obj):
        """Calculate the duration of the operation."""
        if obj.completed_at and obj.started_at:
            return (obj.completed_at - obj.started_at).total_seconds()
        return None

    def get_success_rate(self, obj):
        """Calculate the success rate of the operation."""
        if obj.items_fetched > 0:
            return round((obj.items_saved / obj.items_fetched) * 100, 2)
        return 0.0 