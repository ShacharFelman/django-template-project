from rest_framework import serializers
from example.models import ExampleOfSummary

class ExampleOfModelSerializer(serializers.ModelSerializer):
    """
    Example of a basic model serializer for the ExampleOfSummary model.
    Includes support for status values: 'pending', 'in_progress', 'completed', and 'failed'.
    """
    class Meta:
        model = ExampleOfSummary
        fields = [
            'id', 'processing_model', 'status', 'summary_text', 'word_count', 'processing_cost',
            'created_at', 'completed_at', 'error_message'
        ]
        read_only_fields = fields 