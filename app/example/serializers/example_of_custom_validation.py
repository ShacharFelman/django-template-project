from rest_framework import serializers
from django.utils import timezone
from example.models import ExampleOfArticle

class ExampleOfCustomValidationSerializer(serializers.ModelSerializer):
    """Example of a serializer with custom validation logic."""
    
    def validate_published_date(self, value):
        """
        Example of custom validation: Check that the published date is not in the future.
        """
        if value > timezone.now():
            raise serializers.ValidationError("Published date cannot be in the future.")
        return value

    def validate_title(self, value):
        """
        Example of custom validation: Check that title is not empty and has minimum length.
        """
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return value.strip()

    class Meta:
        model = ExampleOfArticle
        fields = ['id', 'title', 'content', 'url', 'published_date', 'author', 'source', 'image_url', 'description', 'example_source', 'created_at']
        read_only_fields = ['id', 'created_at'] 